import asyncio
import html
import importlib.util
import json
import socket
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

import revel
import uvicorn
import watchfiles
from revel import error, fatal, print, success, warning

import rio.app_server
import rio.cli
import rio.icon_registry
import rio.snippets

from .. import common
from . import nice_traceback, project, snapshot

try:
    import webview  # type: ignore
except ImportError:
    webview = None

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
    <div class="rio-traceback">
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

        # If watching for file changes, this is the task for it
        self._watch_files_task: Optional[asyncio.Task] = None

        # If a webview is being displayed, this is the task for it
        self._webview_task: Optional[asyncio.Task] = None

        # If the arbiter is running, this is the task for it
        self._arbiter_task: Optional[asyncio.Task] = None

        # Released when the app is loaded for the first time, and thus the
        # window should be displayed
        self._show_webview_event = threading.Event()

        # If the uvicorn server is running, this is it
        self._uvicorn_server: Optional[uvicorn.Server] = None

        # If the app is running, this is the `rio.AppServer` instance
        self._app_server: Optional[rio.app_server.AppServer] = None

        # If a webview is being displayed, this is the window
        self._webview_window: Optional["webview.Window"] = None  # type: ignore

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

    def stop(self) -> None:
        """
        Stops the app.
        """
        print("Shutting down")

        # Stop any running tasks
        for task in asyncio.all_tasks():
            task.cancel()

    def run(self) -> None:
        # The webview needs to be shown from the main thread. So, if running
        # inside of a window run the arbiter in a separate thread. Otherwise
        # just run it from this one.

        if self.run_in_window:
            # Make sure the webview module is available
            if webview is None:
                fatal(
                    "The `window` extra is required to run apps inside of a window."
                    " Run `pip install rio[[window]` to install it."
                )

            # Do the thing
            threading.Thread(target=self.arbiter_sync, name="rio run arbiter").start()
            self._show_webview()
        else:
            self.arbiter_sync()

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
            "Rio (debug)"
            if self.debug_mode
            else "Rio",  # TODO: Get the app's name, if possible
            f"http://{self._host}:{self._port}",
        )
        webview.start()

        # Shut everything down
        self._run_in_mainloop(self.stop)

    def arbiter_sync(self) -> None:
        # Print some initial messages
        print()
        print(f"[bold green]{LOGO_TEXT}[/]")
        print()
        print()
        print("Starting")

        # Find a port to run on
        if self._port is None:
            self._port = common.choose_free_port(self._host)
        else:
            if not common.ensure_valid_port(self._host, self._port):
                error(f"The port [bold]{self._port}[/] is already in use.")
                print(f"Each port can only be used by one app at a time.")
                print(
                    f"Try using another port, or let Rio choose one for you, by not specifying any port."
                )
                sys.exit(1)

        # Run
        try:
            asyncio.run(self._arbiter_async())
        except KeyboardInterrupt:
            print()
            print("[yellow]Interrupted[/]")

    async def _arbiter_async(self) -> None:
        # Expose the mainloop, so other threads can interact with asyncio land
        self._mainloop = asyncio.get_running_loop()

        # Start watching for file changes
        if self.debug_mode:
            self._watch_files_task = asyncio.create_task(self._worker_watch_files())

        # Take a snapshot of the current state of the python interpreter
        state_before_app = snapshot.Snapshot()

        # Monotonic timestamp of when the last command was given to restart the
        # app. Any further events which would trigger a reload up to this time
        # can be safely ignored.
        last_reload_started_at = time.monotonic_ns()

        # Start the app for the first time
        await self._start_or_restart_app()

        # Listen for events and react to them
        while True:
            event = await self._event_queue.get()

            # A file has changed
            if isinstance(event, FileChanged):
                # Ignore events that happened before the last reload started
                if event.timestamp < last_reload_started_at:
                    continue

                # Display to the user that a reload is happening
                rel_path = event.path_to_file.relative_to(self.proj.project_directory)
                print()
                print(f"[bold]{rel_path}[/] has changed -> Reloading")

                # Restore the python interpreter to the state it was before the
                # app was started
                state_before_app.restore()

                # Restart the app
                await self._start_or_restart_app()

            # ???
            else:
                raise NotImplementedError(f'Unknown event "{event}"')

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
        async for changes in watchfiles.awatch(self.proj.project_directory):
            for change, path in changes:
                path = Path(path)

                if not self._file_triggers_reload(path):
                    continue

                await self._event_queue.put(
                    FileChanged(
                        time.monotonic_ns(),
                        path,
                    )
                )

    def _import_app_module(self) -> Any:
        """
        Python's importing is bizarre. This function tries to hide all of that
        and imports the module, as specified by the user. This can raise a
        variety of exceptions, since the module's code is evaluated.
        """
        # Path to the module
        module_path = self.proj.module_path

        # Path to the module, as thought of by a drunk python
        if module_path.is_dir():
            import_path = module_path / "__init__.py"
        else:
            import_path = module_path.with_name(module_path.name + ".py")

            if not import_path.exists() or not import_path.is_file():
                raise FileNotFoundError(
                    f"Cannot find any module named `{module_path}` in the project directory `{self.proj.project_directory}`"
                )

        # Import the module
        spec = importlib.util.spec_from_file_location(
            self.proj.app_main_module, import_path
        )
        assert spec is not None, "When does this happen?"

        module = importlib.util.module_from_spec(spec)

        # Register the module
        sys.modules[self.proj.app_main_module] = module

        # Run it
        assert spec.loader is not None, "When does this happen?"
        spec.loader.exec_module(module)

        return module

    def _load_app(self) -> Union[rio.App, BaseException, str]:
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

        # Try to get the app variable
        try:
            app = getattr(app_module, self.proj.app_variable)
        except AttributeError as err:
            error(
                f"Could not find the app variable `{self.proj.app_variable}` in `{self.proj.app_main_module}`"
            )
            return err

        # Make sure the app is indeed a Rio app
        if not isinstance(app, rio.App):
            message = f"The app variable `{self.proj.app_variable}` in `{self.proj.app_main_module}` is not a Rio app, but `{type(app)}`"
            error(message)
            return message

        return app

    async def _spawn_traceback_popups(self, err: Union[str, BaseException]) -> None:
        """
        Displays a popup with the traceback in the rio UI.
        """
        popup_html = make_traceback_html(
            err=err,
            project_directory=self.proj.project_directory,
        )

        await self._evaluate_javascript(
            f"""
// Override the popup with the traceback message
let popup = document.querySelector(".rio-connection-lost-popup");
popup.innerHTML = {json.dumps(popup_html)};

// Spawn the popup
window.setConnectionLostPopupVisible(true);
""",
        )

    async def _start_or_restart_app(
        self,
    ) -> bool:
        """
        Starts the app, or restarts it if it is already running. Returns only
        once the app is ready or failed to start.

        Returns `True` if the app was started successfully, `False` if it
        failed.
        """
        # Load the app
        app = self._load_app()

        if isinstance(app, (str, BaseException)):
            print()
            error("Couldn't load the app. Fix the issue above and try again.")

            if self._uvicorn_server is not None:
                await self._spawn_traceback_popups(app)

            return False

        # Not running yet - start it
        if self._uvicorn_task is None:
            on_ready_event = asyncio.Event()
            self._uvicorn_task = asyncio.create_task(
                self._worker_uvicorn(
                    app,
                    on_ready_or_failed=on_ready_event.set,
                )
            )
            await on_ready_event.wait()

            # The app was just successfully started. Inform the user
            if self.debug_mode:
                warning("Rio is running in DEBUG mode.")
                warning(
                    "Debug mode includes helpful tools for development, but is slower and disables some safety checks. Never use it in production!"
                )
                warning("Run with `--release` to disable debug mode.")

            if not self.run_in_window:
                print()
                print(f"[green]Your app is running at {self._url}[/]")

                if self.public:
                    warning(
                        f"Running in [bold]public[/] mode. All devices on your network can access the app."
                    )
                    warning(f"Only run in public mode if you trust your network!")
                else:
                    print(
                        f"[dim]Running in [bold]local[/] mode. Only this device can access the app.[/]"
                    )

            else:
                success("Ready")

            print()

            # Either open the webview, or a browser
            if self.run_in_window:
                self._webview_task = asyncio.create_task(self._worker_webview())
            else:
                webbrowser.open(self._url)

            return True

        # Already running - restart it
        await self._restart_app(app)
        success("Ready")
        return True

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

        # Create the app server
        app_server = app._as_fastapi(
            debug_mode=self.debug_mode,
            running_in_window=self.run_in_window,
            validator_factory=None,
            internal_on_app_start=lambda: self._run_in_mainloop(
                app_has_started_event.set
            ),
        )

        assert isinstance(app_server, rio.app_server.AppServer), app_server
        self._app_server = app_server

        # Set up a uvicorn server, but don't start it yet
        config = uvicorn.Config(
            self._app_server,
            host=self._host,
            port=self._port,
            log_level="error" if self.quiet else "info",
            timeout_graceful_shutdown=1,  # Without a timeout, sometimes the server just deadlocks
        )
        self._uvicorn_server = uvicorn.Server(config)

        # Run uvicorn in a separate thread
        app_has_started_event: asyncio.Event = asyncio.Event()
        app_has_finished_event: asyncio.Event = asyncio.Event()

        def run_uvicorn() -> None:
            assert self._uvicorn_server is not None
            self._uvicorn_server.run()
            self._run_in_mainloop(app_has_finished_event.set)

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

        except asyncio.CancelledError:
            self._uvicorn_server.should_exit = True

        finally:
            await app_has_finished_event.wait()

    async def _restart_app(
        self,
        app: rio.App,
    ) -> None:
        """
        This function expects that uvicorn is already running. It loads the app
        and injects it into the already running uvicorn server.
        """
        assert self._uvicorn_task is not None, "Can't restart the app without uvicorn"
        assert self._uvicorn_server is not None, "Can't restart the app without uvicorn"
        assert (
            self._app_server is not None
        ), "Can't restart the app without it already running"

        # Inject it into the server
        self._app_server.app = app

        # Tell all sessions to reconnect, and close old sessions
        #
        # This can't use `self._evaluate_javascript` it would race with closing
        # the sessions.
        for sess in list(self._app_server._active_session_tokens.values()):
            # Tell the session to reload
            #
            # TODO: Should there be some waiting period here, so that the
            # session has time to save settings first and shut down in general?
            await self._evaluate_javascript("window.location.reload()")

            # Close it
            asyncio.create_task(
                sess._close(close_remote_session=False),
                name=f'Close session "{sess._session_token}"',
            )

    async def _evaluate_javascript(self, javascript_source: str) -> None:
        """
        Runs the given javascript source in all connected sessions. Does not
        wait for or return the result.
        """
        assert (
            self._app_server is not None
        ), "Can't run javascript without the app running"

        for sess in self._app_server._active_session_tokens.values():

            async def callback() -> None:
                await sess._evaluate_javascript(javascript_source)

            asyncio.create_task(
                callback(),
                name=f"Eval JS in session {sess._session_token}",
            )
