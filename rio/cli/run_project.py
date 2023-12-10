import asyncio
import importlib
import inspect
import os
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

import rio.cli
import rio.snippets

from .. import common
from . import project, snapshot

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
    timestamp: float  # Monothonic timestamp of the change
    path_to_file: Path


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

    @property
    def _host(self) -> str:
        return "0.0.0.0" if self.public else "127.0.0.1"

    @property
    def _url(self) -> str:
        return f"http://{self._host}:{self._port}"

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
        if self._uvicorn_task is not None:
            self._uvicorn_task.cancel()

        if self._watch_files_task is not None:
            self._watch_files_task.cancel()

        if self._webview_task is not None:
            self._webview_task.cancel()

        if self._arbiter_task is not None:
            self._arbiter_task.cancel()

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
        finally:
            webview.stop()

    def _show_webview(self) -> None:
        """
        Keeps the main thread busy until the webview is shown.
        """
        assert webview is not None, "This was already checked before!?"

        # Wait until the server is ready
        self._show_webview_event.wait()

        # Create the window
        window = webview.create_window(
            "Rio (debug)"
            if self.debug_mode
            else "Rio",  # TODO: Get the app's name, if possible
            f"http://{self._host}:{self._port}",
        )
        print("WINDOW", window)
        webview.start()

        # Shut everything down
        self._run_in_mainloop(self.stop)

    def arbiter_sync(self) -> None:
        # Print some initial messages
        print()
        print(f"[bold primary]{LOGO_TEXT}[/]")
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
        app_ready_event = asyncio.Event()

        self._uvicorn_task = asyncio.create_task(
            self._worker_uvicorn(
                on_ready=app_ready_event.set,
            )
        )
        await app_ready_event.wait()

        # Inform the user how to connect
        print()
        print(f"[green]Your app is running at {self._url}[/]")

        if self.public:
            warning(
                f"Running in [bold]public[/] mode. All devices on your network can access the app."
            )
            warning(f"Only run in public mode if you trust your network")
        else:
            print(
                f"[dim]Running in [bold]local[/] mode. Only this device can access the app.[/]"
            )

        print()

        # The app is ready. Either open the webview, or a browser
        if self.run_in_window:
            self._webview_task = asyncio.create_task(self._worker_webview())
        else:
            webbrowser.open(self._url)

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

                # Stop the app, if it's running
                if self._uvicorn_task is not None:
                    print("Stopping app")
                    self._uvicorn_task.cancel()

                    try:
                        await self._uvicorn_task
                    except asyncio.CancelledError:
                        pass

                # Restore the python interpreter to the state it was before the
                # app was started
                state_before_app.restore()

                # Start the app again
                print("Restarting app")
                app_ready_event = asyncio.Event()

                last_reload_started_at = time.monotonic_ns()
                self._uvicorn_task = asyncio.create_task(
                    self._worker_uvicorn(
                        on_ready=lambda: self._run_in_mainloop(
                            app_ready_event.set,
                        ),
                    )
                )

                # Wait for the app to be ready
                await app_ready_event.wait()
                success("Ready")

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

    async def _worker_uvicorn(
        self,
        *,
        on_ready: Callable[[], None],
    ) -> None:
        """
        Runs the app. It will serve the latest version of the project on the
        specified host and port.

        The function returns only once the app does.
        """
        # Import the app module
        try:
            app_module = importlib.import_module(self.proj.main_module)
        except Exception as e:
            error(f"Could not import `{self.proj.main_module}`: {e}")
            on_ready()
            return

        # Try to get the app variable
        try:
            app = getattr(app_module, self.proj.app_variable)
        except AttributeError:
            error(
                f"Could not find the app variable `{self.proj.app_variable}` in `{self.proj.main_module}`"
            )
            on_ready()
            return

        # Make sure the app is indeed a Rio app
        if not isinstance(app, rio.App):
            error(
                f"The app variable `{self.proj.app_variable}` in `{self.proj.main_module}` is not a Rio app, but `{type(app)}`"
            )
            on_ready()
            return

        # The port has been set before
        assert self._port is not None

        import socket

        global our_socket

        print("creating socket")
        our_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # our_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        our_socket.bind((self._host, self._port))
        our_socket.listen(5)

        # Set up a uvicorn server, but don't start it yet
        config = uvicorn.Config(
            app._as_fastapi(
                debug_mode=self.debug_mode,
                running_in_window=False,  # TODO
                validator_factory=None,
                internal_on_app_start=lambda: self._run_in_mainloop(
                    app_has_started_event.set
                ),
            ),
            host=self._host,
            port=self._port,
            log_level="error" if self.quiet else "info",
            timeout_graceful_shutdown=1,  # Without a timeout, sometimes the server just deadlocks
        )
        uvicorn_server = uvicorn.Server(config)

        # Run uvicorn in a separate thread
        app_has_started_event: asyncio.Event = asyncio.Event()
        app_has_finished_event: asyncio.Event = asyncio.Event()

        def run_uvicorn() -> None:
            uvicorn_server.run(sockets=[our_socket])
            self._run_in_mainloop(app_has_finished_event.set)

        uvicorn_thread = threading.Thread(target=run_uvicorn)
        uvicorn_thread.start()

        try:
            # Wait for the app to be ready
            await app_has_started_event.wait()

            # Trigger the event
            on_ready()

            # Wait for either the app to stop, or until the task is canceled
            wait_forever_event = asyncio.Event()
            await wait_forever_event.wait()

        except asyncio.CancelledError:
            uvicorn_server.should_exit = True

        finally:
            await app_has_finished_event.wait()

            # Reuse the same socket
            our_socket.close()

            # Wait for the port to be released
            while not common.ensure_valid_port(self._host, self._port):
                await asyncio.sleep(0.1)
