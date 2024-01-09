import asyncio
import html
import importlib
import inspect
import json
import logging
import signal
import socket
import sys
import threading
import time
import traceback
import types
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

import uvicorn
import watchfiles
from revel import error, fatal, print, success, warning

import rio.app_server
import rio.cli
import rio.icon_registry
import rio.snippets

from .. import common, debug
from . import nice_traceback, project

try:
    import webview  # type: ignore
except ImportError:
    webview = None


# There is a hillarious problem with `watchfiles`: When a change occurs,
# `watchfiles` logs that change. If Python is configured to log into the project
# directory, then `watchfiles` will pick up on that new log line, thus
# triggering another change. Infinite loop, here we come!
#
# -> STFFU, watchfiles!
logging.getLogger("watchfiles").setLevel(logging.CRITICAL + 1)


LOGO_TEXT = r"""  _____  _
 |  __ \(_)
 | |__) |_  ___
 |  _  /| |/ _ \
 | | \ \| | (_) |
 |_|  \_\_|\___/"""


class Event:
    pass


@dataclass
class FileChanged(Event):
    timestamp: float  # Monotonic timestamp of the change
    path_to_file: Path


def make_traceback_html(
    *,
    err: Union[str, BaseException],
    project_directory: Path,
) -> str:
    icon_registry = rio.icon_registry.IconRegistry.get_singleton()
    error_icon_svg = icon_registry.get_icon_svg("error")

    if isinstance(err, str):
        traceback_html = html.escape(err)
    else:
        traceback_html = nice_traceback.format_exception_html(
            err,
            relpath=project_directory,
        )

    return f"""
<div>
    <div class="rio-traceback rio-debugger-background rio-switcheroo-neutral">
        <div class="rio-traceback-header">
            {error_icon_svg}
            <div>Couldn't load the app</div>
        </div>
        <div class="rio-traceback-message">
            Fix the issue below. The app will automatically reload once you save the
            file.
        </div>
        <div class="rio-traceback-traceback">{traceback_html}</div>
        <div class="rio-traceback-footer">
            Need help?
            <div class="rio-traceback-footer-links">
                <a class="rio-text-link" target="_blank" href="https://todo.discord.com">Ask on our Discord</a>
                <a class="rio-text-link" target="_blank" href="https://chat.openai.com">Ask ChatGPT</a>
                <a class="rio-text-link" target="_blank" href="https://rio.dev/documentation">Read the docs</a>
            </div>
        </div>
    </div>
</div>
"""


class RunningApp:
    def __init__(
        self,
        *,
        proj: project.RioProject,
        port: Optional[int],
        public: bool,
        quiet: bool,
        debug_mode: bool,
        run_in_window: bool,
    ) -> None:
        assert not (
            run_in_window and public
        ), "Can't run in a local window over the network, wtf!?"

        self.proj = proj
        self._port = port
        self.public = public
        self.quiet = quiet
        self.debug_mode = debug_mode
        self.run_in_window = run_in_window

        # Contains any changes that need to be applied to the project
        self._event_queue: asyncio.Queue[Event] = asyncio.Queue()

        # If running, the asyncio mainloop
        self._mainloop: Optional[asyncio.AbstractEventLoop] = None

        # If the app is currently running, this is the task for it
        self._uvicorn_task: Optional[asyncio.Task] = None

        # If the webview is running, this is the task responsible for shutting
        # it down
        self._webview_task: Optional[asyncio.Task] = None

        # Released when the app is loaded for the first time, and thus the
        # window should be displayed
        self._show_webview_event = threading.Event()

        # If the uvicorn server is running, this is it
        self._uvicorn_server: Optional[uvicorn.Server] = None

        # If the app is running, this is the `rio.AppServer` instance
        self._app_server: Optional[rio.app_server.AppServer] = None

        # If a webview is being displayed, this is the window
        self._webview_window: Optional["webview.Window"] = None  # type: ignore

        # The app to use for creating apps. This keeps the theme consistent if
        # for-example the user's app crashes and then a mock-app is injected.
        self._app_theme: Union[
            rio.Theme, Tuple[rio.Theme, rio.Theme]
        ] = rio.Theme.from_color()

        # A list of worker tasks that must shut down gracefully. That means the
        # asyncio event loop mustn't stop running until these tasks are done.
        self._workers: list[asyncio.Task] = []

    @property
    def _host(self) -> str:
        return "0.0.0.0" if self.public else "127.0.0.1"

    @property
    def _url(self) -> str:
        if self.public:
            # Get the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(
                ("8.8.8.8", 80)
            )  # Doesn't send data, because UDP is connectionless
            local_ip = s.getsockname()[0]
            s.close()
        else:
            local_ip = "127.0.0.1"

        return f"http://{local_ip}:{self._port}"

    def make_error_message_app(self, err: Union[str, BaseException]) -> rio.App:
        """
        Creates an app that displays the given error message.
        """
        html = make_traceback_html(
            err=err,
            project_directory=self.proj.project_directory,
        )

        return rio.App(
            build=lambda: rio.Html(html),
            theme=self._app_theme,
        )

    def _create_worker(
        self, worker_coro: Coroutine, *, name: str | None = None
    ) -> asyncio.Task:
        task = asyncio.create_task(worker_coro, name=name)
        self._workers.append(task)
        return task

    def _run_in_mainloop(
        self,
        callback: Callable[[], None],
    ) -> None:
        """
        Calls the given function in the asyncio mainloop, as task.
        """
        assert (
            self._mainloop is not None
        ), "Cannot use this function before asyncio is running"
        assert (
            self._mainloop.is_running()
        ), "Cannot use this function before asyncio is running"

        # Run the function in the mainloop
        self._mainloop.call_soon_threadsafe(callback)

    def _on_sigint(self, signal_id, stack_frame) -> None:
        self.stop(keyboard_interrupt=True)

    def stop(self, *, keyboard_interrupt: bool) -> None:
        """
        Stops the app.
        """

        if keyboard_interrupt:
            print()
            print("[yellow]Interrupted[/]")
        else:
            print("Shutting down")

        # Stop any running tasks
        self._run_in_mainloop(self._cancel_all_tasks)

    def _cancel_all_tasks(self) -> None:
        for task in asyncio.all_tasks():
            task.cancel()

    def run(self) -> None:
        # Before we do anything else, ensure that the `rio.toml` contains all
        # the required information. This will load and cache all the information
        # we need, or crash with `revel.fatal()`. Either way, it ensures that
        # `revel.fatal()` won't be called *while* we're trying to process the
        # `rio.toml`.
        self._cache_data_from_rio_toml()

        # Handle keyboard interrupts. KeyboardInterrupt exceptions are very
        # annoying to handle in async code, so instead we'll use a signal
        # handler.
        signal.signal(signal.SIGINT, self._on_sigint)

        # If running in debug mode, install safeguards
        if self.debug_mode:
            debug.apply_monkeypatches()

        # The webview needs to be shown from the main thread. So, if running
        # inside of a window run the arbiter in a separate thread. Otherwise
        # just run it from this one.
        if self.run_in_window:
            # Make sure the webview module is available
            if webview is None:
                fatal(
                    "The `window` extra is required to run apps inside of a window."
                    " Run `pip install rio-ui[[window]` to install it."
                )

            # Do the thing
            threading.Thread(target=self.arbiter_sync, name="rio run arbiter").start()
            self._show_webview()
        else:
            self.arbiter_sync()

    def _cache_data_from_rio_toml(self) -> None:
        _ = self.proj.app_main_module

    async def _worker_webview(self) -> None:
        """
        Shows the webview when called. Closes it when canceled.

        Since webview requires the webview to be shown from the main thread, it
        is already running in a separate thread. This function just controls it,
        making it appear async.
        """
        assert not self._show_webview_event.is_set(), "This was already called!?"
        assert webview is not None

        # Show the webview
        self._show_webview_event.set()

        # Wait until this task is canceled
        wait_forever_event = asyncio.Event()

        try:
            await wait_forever_event.wait()

        # Clean up
        #
        # Wait for the window to actually be created first
        finally:
            while self._webview_window is None:
                await asyncio.sleep(0.1)

            self._webview_window.destroy()

    def _show_webview(self) -> None:
        """
        Keeps the main thread busy until the webview is shown.
        """
        assert webview is not None, "This was already checked before!?"

        # Wait until the server is ready
        self._show_webview_event.wait()

        # Create the window
        self._webview_window = webview.create_window(
            # TODO: Get the app's name, if possible
            "Rio (debug)" if self.debug_mode else "Rio",
            f"http://{self._host}:{self._port}",
        )
        webview.start()

        # If the webview window is closed, shut down.
        #
        # One problem: We don't know if the webview stopped because the user
        # closed the window or because the webview worker was cancelled and
        # called `window.close()`. If the user closed the webview window, then
        # we're responsible for shutting down all the workers.
        assert self._webview_task is not None
        if not self._webview_task.cancelled():
            self.stop(keyboard_interrupt=False)

    def arbiter_sync(self) -> None:
        # Print some initial messages
        print()
        print(f"[bold green]{LOGO_TEXT}[/]")
        print()
        print()
        print("Starting")

        # Find a port to run on
        #
        # Prefer to consistently run on the same port, as that makes it easier
        # to connect to - this way old browser tabs don't get invalidated constantly.
        if self._port is None:
            if common.port_is_free(self._host, 8000):
                self._port = 8000
            else:
                self._port = common.choose_free_port(self._host)

        # If a port is specified, use that. Just make sure it's free.
        else:
            if not common.ensure_valid_port(self._host, self._port):
                error(f"The port [bold]{self._port}[/] is already in use.")
                print(f"Each port can only be used by one app at a time.")
                print(
                    f"Try using another port, or let Rio choose one for you, by not specifying any port."
                )
                sys.exit(1)

        # Run
        asyncio.run(self._arbiter_async())

    async def _arbiter_async(self) -> None:
        try:
            # Expose the mainloop, so other threads can interact with asyncio land
            self._mainloop = asyncio.get_running_loop()

            # Start watching for file changes
            if self.debug_mode:
                self._create_worker(self._worker_watch_files())

            # Monotonic timestamp of when the last command was given to restart the
            # app. Any further events which would trigger a reload up to this time
            # can be safely ignored.
            last_reload_started_at = time.monotonic_ns()

            # Start the app for the first time
            await self._start_app()

            # The app was just successfully started. Inform the user
            if self.debug_mode:
                print()
                warning("Rio is running in DEBUG mode.")
                warning(
                    "Debug mode includes helpful tools for development, but is slower and disables some safety checks. Never use it in production!"
                )
                warning("Run with `--release` to disable debug mode.")

            # Listen for events and react to them
            while True:
                event = await self._event_queue.get()

                # A file has changed
                if isinstance(event, FileChanged):
                    # Ignore events that happened before the last reload started
                    if event.timestamp < last_reload_started_at:
                        continue

                    # Display to the user that a reload is happening
                    rel_path = event.path_to_file.relative_to(
                        self.proj.project_directory
                    )
                    print()
                    print(f"[bold]{rel_path}[/] has changed -> Reloading")

                    # Restart the app
                    await self._restart_app()

                # ???
                else:
                    raise NotImplementedError(f'Unknown event "{event}"')
        except asyncio.CancelledError:
            pass
        finally:
            # When the arbiter exits, the asyncio event loop shuts down. We don't
            # want that to happen until all our workers have shut down. Wait for
            # them to finish.
            for worker in self._workers:
                try:
                    await worker
                except asyncio.CancelledError:
                    pass

    def _file_triggers_reload(self, path: Path) -> bool:
        if path.suffix == ".py":
            return True

        if path.name in ("rio.toml",):
            return True

        return False

    async def _worker_watch_files(self) -> None:
        """
        Watch the project directory for changes and report them as events.
        """
        filter = watchfiles.PythonFilter()

        async for changes in watchfiles.awatch(
            self.proj.project_directory, watch_filter=filter
        ):
            for change, path in changes:
                path = Path(path)

                if not self._file_triggers_reload(path):
                    continue

                file_changed = FileChanged(
                    time.monotonic_ns(),
                    path,
                )
                await self._event_queue.put(file_changed)

    def _import_app_module(self) -> types.ModuleType:
        """
        Python's importing is bizarre. This function tries to hide all of that
        and imports the module, as specified by the user. This can raise a
        variety of exceptions, since the module's code is evaluated.
        """
        # Purge the module from the module cache
        app_main_module = self.proj.app_main_module
        root_module, _, _ = app_main_module.partition(".")

        for module_name in list(sys.modules):
            if module_name.partition(".")[0] == root_module:
                del sys.modules[module_name]

        # Now (re-)import the app module
        sys.path.append(str(self.proj.module_path.parent))

        try:
            return importlib.import_module(app_main_module)
        finally:
            # TODO: What if the user themselves appends to `sys.path`?
            del sys.path[-1]

    def _load_app(self) -> rio.App | str | BaseException:
        # Import the app module
        try:
            app_module = self._import_app_module()
        except BaseException as err:
            error(f"Could not import `{self.proj.app_main_module}`:")
            print(
                nice_traceback.format_exception_revel(
                    err,
                    relpath=self.proj.project_directory,
                )
            )
            return err

        # Find the variable holding the Rio app
        apps: List[Tuple[str, rio.App]] = []
        for var_name, var in app_module.__dict__.items():
            if isinstance(var, rio.App):
                apps.append((var_name, var))

        if app_module.__file__ is None:
            main_file_reference = f"Your app's main file"
        else:
            main_file_reference = f"The file `{Path(app_module.__file__).relative_to(self.proj.project_directory)}`"

        if len(apps) == 0:
            message = f"Cannot find your app. {main_file_reference} needs to to define a variable that is a Rio app. Something like `app = rio.App(...)`"
            error(message)
            return message

        if len(apps) > 1:
            variables_string = "`" + "`, `".join(var_name for var_name, _ in apps) + "`"
            message = f"{main_file_reference} defines multiple Rio apps: {variables_string}. Please make sure there is exactly one."
            error(message)
            return message

        app = apps[0][1]

        # Remember the app's theme
        self._app_theme = app._theme

        # Explicitly set the asset directory because it can't reliably be
        # auto-detected
        module_path = self.proj.module_path
        if module_path.is_file():
            module_path = module_path.parent
        app.assets_dir = module_path / app._assets_dir

        return app

    def _spawn_traceback_popups(self, err: Union[str, BaseException]) -> None:
        """
        Displays a popup with the traceback in the rio UI.
        """
        popup_html = make_traceback_html(
            err=err,
            project_directory=self.proj.project_directory,
        )

        self._evaluate_javascript_in_all_sessions(
            f"""
// Override the popup with the traceback message
let popup = document.querySelector(".rio-connection-lost-popup");
popup.innerHTML = {json.dumps(popup_html)};

// Spawn the popup
window.setConnectionLostPopupVisible(true);
""",
        )

    async def _start_app(self) -> None:
        """
        Starts uvicorn and the app. Returns only once the app is ready.

        If the user's code can't be imported, a dummy app displaying the error
        message will be created.
        """
        # Load the app
        app_or_error = self._load_app()

        if isinstance(app_or_error, rio.App):
            app = app_or_error
        else:
            app = self.make_error_message_app(app_or_error)

        # Start uvicorn
        on_ready_event = asyncio.Event()
        self._uvicorn_task = self._create_worker(
            self._worker_uvicorn(
                app,
                on_ready_or_failed=on_ready_event.set,
            )
        )
        await on_ready_event.wait()

        print()
        if self.run_in_window:
            success("Ready")
            self._webview_task = self._create_worker(self._worker_webview())
        else:
            success(f"Your app is running at {self._url}")

            if self.public:
                warning(
                    f"Running in [bold]public[/] mode. All devices on your network can access the app."
                )
                warning(f"Only run in public mode if you trust your network!")
            else:
                print(
                    f"[dim]Running in [/]local[dim] mode. Only this device can access the app.[/]"
                )

            webbrowser.open(self._url)

    async def _worker_uvicorn(
        self,
        app: rio.App,
        *,
        on_ready_or_failed: Callable[[], None],
    ) -> None:
        """
        Runs the app. It will serve the latest version of the project on the
        specified host and port.

        The function returns only once the app does.
        """
        assert self._port is not None
        assert self._uvicorn_server is None, "Can't start the server twice"
        assert self._app_server is None, "Can't start the server twice"

        def start_callback() -> None:
            print("Debug: Internal on app start")
            self._run_in_mainloop(app_has_started_event.set)

        # Create the app server
        print("Debug: As fastapi")
        app_server = app._as_fastapi(
            debug_mode=self.debug_mode,
            running_in_window=self.run_in_window,
            validator_factory=None,
            internal_on_app_start=start_callback,
        )
        print("Debug: After as fastapi")

        assert isinstance(app_server, rio.app_server.AppServer), app_server
        self._app_server = app_server

        # Set up a uvicorn server, but don't start it yet
        config = uvicorn.Config(
            self._app_server,
            host=self._host,
            port=self._port,
            log_level="error" if self.quiet else "info",
            timeout_graceful_shutdown=1,  # Without a timeout the server sometimes deadlocks
        )
        self._uvicorn_server = uvicorn.Server(config)

        # Run uvicorn in a separate thread
        app_has_started_event: asyncio.Event = asyncio.Event()

        def run_uvicorn() -> None:
            assert self._uvicorn_server is not None
            self._uvicorn_server.run()
            # Nothing to do here. If the server stops running, it's because we
            # told it to - that means the program is already shutting down.

        uvicorn_thread = threading.Thread(target=run_uvicorn)
        uvicorn_thread.start()

        try:
            # Wait for the app to be ready
            await app_has_started_event.wait()

            # Trigger the event
            on_ready_or_failed()

            # Wait for either the app to stop, or until the task is canceled
            wait_forever_event = asyncio.Event()
            await wait_forever_event.wait()

        finally:
            self._uvicorn_server.should_exit = True

    async def _restart_app(self) -> None:
        """
        This function expects that uvicorn is already running. It loads the app
        and injects it into the already running uvicorn server.
        """
        assert self._uvicorn_task is not None, "Can't restart the app without uvicorn"
        assert self._uvicorn_server is not None, "Can't restart the app without uvicorn"
        assert (
            self._app_server is not None
        ), "Can't restart the app without it already running"

        # Reload the app
        app_or_error = self._load_app()

        if isinstance(app_or_error, rio.App):
            app = app_or_error
        else:
            if self._uvicorn_server is not None:
                self._spawn_traceback_popups(app_or_error)

            app = self.make_error_message_app(app_or_error)

        # Inject the app into the server
        self._app_server.app = app

        # Re-run the `on_app_start` callback
        await self._app_server._call_on_app_start()

        # Tell all sessions to reconnect, and close old sessions
        #
        # This can't use `self._evaluate_javascript`, it would race with closing
        # the sessions.
        for sess in list(self._app_server._active_session_tokens.values()):
            # Tell the session to reload
            #
            # TODO: Should there be some waiting period here, so that the
            # session has time to save settings first and shut down in general?
            await sess._evaluate_javascript("window.location.reload()")

            # Close it
            asyncio.create_task(
                sess._close(close_remote_session=False),
                name=f'Close session "{sess._session_token}"',
            )

        # The app has changed, but the uvicorn server is still the same. Because
        # of this, uvicorn won't call the `on_app_start` function - do it
        # manually.
        if app._on_app_start is not None:
            try:
                result = app._on_app_start(app)

                if inspect.isawaitable(result):
                    await result

            # Display and discard exceptions
            except Exception:
                print("Exception in `on_app_start` event handler:")
                traceback.print_exc()

    def _evaluate_javascript_in_all_sessions(self, javascript_source: str) -> None:
        """
        Runs the given javascript source in all connected sessions. Does not
        wait for or return the result.
        """
        assert (
            self._app_server is not None
        ), "Can't run javascript without the app running"

        async def evaljs_as_coroutine(sess: rio.Session) -> None:
            await sess._evaluate_javascript(javascript_source)

        for sess in self._app_server._active_session_tokens.values():
            asyncio.create_task(
                evaljs_as_coroutine(sess),
                name=f"Eval JS in session {sess._session_token}",
            )  #
