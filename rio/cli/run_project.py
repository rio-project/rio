import asyncio
import importlib
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
        release: bool,
    ) -> None:
        self.proj = proj
        self._port = port
        self.public = public
        self.quiet = quiet
        self.release = release

        # If the app is currently running, this is the task for it
        self._running_app_task: Optional[asyncio.Task] = None

        # Contains any changes that need to be applied to the project
        self._event_queue: asyncio.Queue[Event] = asyncio.Queue()

        # A list of running tasks belonging to this `RunningApp`
        self._running_tasks: List[asyncio.Task] = []

        # The snapshot of the python interpreter when the app was started
        self._snapshot: Optional[snapshot.Snapshot] = None

        # If running, the current uvicorn server
        self._uvicorn_server: Optional[uvicorn.Server] = None

    @property
    def _host(self) -> str:
        return "0.0.0.0" if self.public else "127.0.0.1"

    def _setup_cli_screen(self) -> None:
        print()
        print(f"[bold primary]{LOGO_TEXT}[/]")
        print()
        print()

    def run(self) -> None:
        # Initialize
        self._setup_cli_screen()

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
            asyncio.run(self._arbiter_task())

        except KeyboardInterrupt:
            print("[yellow]Interrupted[/]")

        # Clean up
        finally:
            print("Shutting down")
            if self._uvicorn_server is not None:
                self._uvicorn_server.should_exit = True

            for task in self._running_tasks:
                task.cancel()

        # Force exit, so no bugs in the app can keep the process alive
        sys.exit(0)

    def _file_triggers_reload(self, path: Path) -> bool:
        if path.suffix == ".py":
            return True

        if path.name in ("rio.toml",):
            return True

        return False

    async def _watcher_task(self) -> None:
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

    async def _run_app_server(self) -> None:
        assert self._uvicorn_server is None, "The uvicorn server is already running!?"

        # Import the app module
        try:
            app_module = importlib.import_module(self.proj.main_module)
        except Exception as e:
            error(f"Could not import `{self.proj.main_module}`: {e}")
            return

        # Try to get the app variable
        try:
            app = getattr(app_module, self.proj.app_variable)
        except AttributeError:
            error(
                f"Could not find the app variable `{self.proj.app_variable}` in `{self.proj.main_module}`"
            )
            return

        # Make sure the app is indeed a Rio app
        if not isinstance(app, rio.App):
            error(
                f"The app variable `{self.proj.app_variable}` in `{self.proj.main_module}` is not a Rio app, but `{type(app)}`"
            )
            return

        # Run the app
        ready_lock = asyncio.Lock()
        await ready_lock.acquire()

        def run_uvicorn() -> None:
            # The port has been set before
            assert self._port is not None
            assert self._uvicorn_server is None

            # Set up a uvicorn server
            config = uvicorn.Config(
                app._as_fastapi(
                    running_in_window=False,  # TODO
                    validator_factory=None,
                    internal_on_app_start=ready_lock.release,
                ),
                host=self._host,
                port=self._port,
                log_level="error" if self.quiet else "info",
                timeout_graceful_shutdown=1,  # Without a timeout, sometimes the server just deadlocks
            )
            self._uvicorn_server = uvicorn.Server(config)
            self._uvicorn_server.run()

        uvicorn_thread = threading.Thread(target=run_uvicorn)
        uvicorn_thread.start()

        # Wait for the app to be ready
        await ready_lock.acquire()

    async def _restart_app_server(self) -> None:
        """
        Start/Restart the app. It will serve the latest version of the project
        on the specified host and port.
        """
        # Stop the old app, if it's running
        if self._running_app_task is not None:
            print("Stopping app server")
            self._running_app_task.cancel()

        # Restore the python interpreter to the state it was in when the app was
        # started
        self.snapshot.restore()

        # Start the new app
        print("Starting app")
        self._running_app_task = await self._run_app_server()

        # Done!
        success("App is ready")
        success("[bold]Running[/]")

    async def _arbiter_task(self) -> None:
        # Start watching for file changes
        if not self.release:
            watcher_task = asyncio.create_task(
                self._watcher_task(), name="rio run: file watcher"
            )
            self._running_tasks.append(watcher_task)

        # Take a snapshot of the current state of the python interpreter
        self.snapshot = snapshot.Snapshot()

        # Monotonic timestamp of when the last command was given to restart the
        # app. Any further events which would trigger a reload up to this time
        # can be safely ignored.
        last_reload_started_at = time.monotonic_ns()

        # Start the app for the first time
        await self._restart_app_server()

        # Inform the user how to connect
        host = "0.0.0.0" if self.public else "127.0.0.1"
        app_url = f"http://{host}:{self._port}"

        print()
        print(f"[green]Your app is running at {app_url}[/]")

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
        webbrowser.open(app_url)

        # Listen for events and react to them
        while True:
            event = await self._event_queue.get()

            # A file has changed
            if isinstance(event, FileChanged):
                # Ignore events that happened before the last reload started
                if event.timestamp < last_reload_started_at:
                    continue

                # Reload the app
                last_reload_started_at = time.monotonic_ns()

                rel_path = event.path_to_file.relative_to(self.proj.project_directory)
                print()
                print(f"[bold]{rel_path}[/] has changed -> Reloading")
                warning("Reloading")

                await self._restart_app_server()

            else:
                raise NotImplementedError(f'Unknown event "{event}"')
