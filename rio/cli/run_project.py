import asyncio
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
from typing_extensions import TypeAlias

import rio.cli
import rio.snippets

from .. import common
from . import project

__all__ = [
    "run_project",
]


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
    ) -> None:
        self.proj = proj
        self.port = port
        self.public = public

        # If the app is currently running, this is the task for it
        self._running_app_task: Optional[asyncio.Task] = None

        # Contains any changes that need to be applied to the project
        self._event_queue: asyncio.Queue[Event] = asyncio.Queue()

        # A revel text line that's docket to the bottom of the terminal. Set via
        # `_set_status`
        self._status_line: revel.TextLine = revel.TextLine()  # Just a placeholder

        # A list of running tasks belonging to this `RunningApp`
        self._running_tasks: List[asyncio.Task] = []

    def _set_status(
        self,
        text: str,
        *,
        level: Literal["success", "info", "warning", "error"] = "info",
    ) -> None:
        if level == "success":
            color = "[green]"
        elif level == "info":
            color = "[]"
        elif level == "warning":
            color = "[yellow]"
        else:
            assert level == "error"
            color = "[red]"

        self._status_line.text = f"{color}{text}[/]"

    def _setup_cli_screen(self) -> None:
        print()
        print(f"[bold primary]{LOGO_TEXT}[/]")
        print()
        print()
        self._status_line = print("Preparing", dock=True)

    def run(self) -> None:
        # Initialize
        self._setup_cli_screen()

        # Find a port to run on
        host = "0.0.0.0" if self.public else "127.0.0.1"
        if self.port is None:
            self.port = common.choose_free_port(host)
        else:
            if not common.ensure_valid_port(host, self.port):
                error(f"The port [bold]{self.port}[/] is already in use.")
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
            self._set_status("Shutting down")
            for task in self._running_tasks:
                task.cancel()

            self._status_line.undock()

        # Force exit, so no bugs in the app can keep the process alive
        sys.exit(0)

    async def _watcher_task(self) -> None:
        """
        Watch the project directory for changes and report them as events.
        """
        async for changes in watchfiles.awatch(self.proj.project_directory):
            for change, path in changes:
                path = Path(path)
                if path.suffix != ".py":
                    continue

                await self._event_queue.put(
                    FileChanged(
                        time.monotonic(),
                        path,
                    )
                )

    async def _run_app_server(self, on_ready_lock: asyncio.Lock) -> None:
        await asyncio.sleep(3)  # TODO
        on_ready_lock.release()

    async def _restart_app_server(self) -> None:
        """
        Start/Restart the app. It will serve the latest version of the project
        on the specified host and port.
        """
        # Stop the old app, if it's running
        if self._running_app_task is not None:
            self._set_status("Stopping app server")
            self._running_app_task.cancel()

        # Start the new app
        self._set_status("Starting app")
        ready_lock = asyncio.Lock()
        await ready_lock.acquire()
        self._running_app_task = asyncio.create_task(
            self._run_app_server(ready_lock), name="rio run: app server"
        )

        self._running_tasks.append(self._running_app_task)

        # Wait for the app to be ready
        await ready_lock.acquire()

        # Done!
        success("App is ready")
        self._set_status("[bold]Running[/]", level="success")

    async def _arbiter_task(self) -> None:
        # Start watching for file changes
        watcher_task = asyncio.create_task(
            self._watcher_task(), name="rio run: file watcher"
        )
        self._running_tasks.append(watcher_task)

        # Monotonic timestamp of when the last command was given to restart the
        # app. Any further events which would trigger a reload up to this time
        # can be safely ignored.
        last_reload_started_at = time.monotonic()

        # Start the app for the first time
        await self._restart_app_server()

        # Inform the user how to connect
        host = "0.0.0.0" if self.public else "127.0.0.1"
        app_url = f"http://{host}:{self.port}"
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
                last_reload_started_at = time.monotonic()
                rel_path = event.path_to_file.relative_to(self.proj.project_directory)
                print()

                print(f"[bold]{rel_path}[/] has changed -> Reloading")
                self._set_status("Reloading", level="warning")

                await self._restart_app_server()

            else:
                raise NotImplementedError(f'Unknown event "{event}"')
