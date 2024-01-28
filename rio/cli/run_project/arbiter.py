import asyncio
import html
import json
import logging
import os
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

import revel
import uvicorn
import watchfiles
from revel import debug, error, fatal, print, success, warning

import rio.app_server
import rio.cli
import rio.icon_registry
import rio.snippets

from ... import common
from ...debug.monkeypatches import apply_monkeypatches
from .. import nice_traceback, project
from . import (
    app_loading,
    file_watcher_worker,
    run_models,
    run_utils,
    uvicorn_worker,
    webview_worker,
)

try:
    import webview  # type: ignore
except ImportError:
    if TYPE_CHECKING:
        import webview  # type: ignore
    else:
        webview = None


# There is a hilarious problem with `watchfiles`: When a change occurs,
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


class Arbiter:
    """
    Serves as a unified interface to running apps, coordinating the various
    workers necessary to do so.
    """

    def __init__(
        self,
        *,
        proj: project.RioProject,
        port: int | None,
        public: bool,
        quiet: bool,
        debug_mode: bool,
        run_in_window: bool,
    ) -> None:
        assert not (
            run_in_window and public
        ), "Can't run in a local window over the network, wtf!?"

        self.proj = proj
        self.public = public
        self.quiet = quiet
        self.debug_mode = debug_mode
        self.run_in_window = run_in_window

        # Workers communicate with the `RunningApp` by pushing events into this
        # queue.
        self._event_queue: asyncio.Queue[run_models.Event] = asyncio.Queue()

        # If running, contains the various workers
        self._file_watcher_worker: file_watcher_worker.FileWatcherWorker | None = None
        self._uvicorn_worker: uvicorn_worker.UvicornWorker | None = None
        self._webview_worker: webview_worker.WebViewWorker | None = None

        self._file_watcher_task: asyncio.Task[None] | None = None
        self._uvicorn_task: asyncio.Task[None] | None = None

        # The app to use for creating apps. This keeps the theme consistent if
        # for-example the user's app crashes and then a mock-app is injected.
        self._app_theme: Union[
            rio.Theme, tuple[rio.Theme, rio.Theme]
        ] = rio.Theme.pair_from_color()

        # Prefer to consistently run on the same port, as that makes it easier
        # to connect to - this way old browser tabs don't get invalidated
        # constantly.
        if port is None:
            if common.port_is_free(self._host, 8000):
                self.port = 8000
            else:
                self.port = common.choose_free_port(self._host)
        else:
            self.port = port

        # Used by the stop function for thread safety
        self._stopping_lock = threading.Lock()

        # This future resolves once the app is ready to be shown in the webview.
        # Wait for it.
        self._server_is_ready = threading.Event()

        # Used to signal that the app should close
        self._stop_requested = threading.Event()

        # The mainloop used by the arbiter. This is set once asyncio is running.
        self._mainloop: asyncio.AbstractEventLoop | None = None

    def push_event(self, event: run_models.Event) -> None:
        """
        Pushes an event into the event queue. Threadsafe.
        """
        assert self._mainloop is not None, "Can't push events before asyncio is running"
        self._mainloop.call_soon_threadsafe(self._event_queue.put_nowait, event)

    @property
    def _host(self) -> str:
        return "0.0.0.0" if self.public else "127.0.0.1"

    @property
    def url(self) -> str:
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

        return f"http://{local_ip}:{self.port}"

    def stop(self, *, keyboard_interrupt: bool) -> None:
        """
        Stops the app. This function can safely be called more than once, and at
        any point in time.
        """
        # Already shutting down? Then do nothing
        if not self._stopping_lock.acquire(blocking=False):
            return

        # Visualize KeyboardInterrupts
        if keyboard_interrupt:
            print()
            print("[yellow]Interrupted[/]")
        else:
            print("Shutting down")

        # Release anyone waiting for events
        self._stop_requested.set()
        self._server_is_ready.set()

        # Stop any running workers
        assert self._mainloop is not None, "Mainloop isn't running!?"

        def cancel_all_tasks() -> None:
            for task in asyncio.all_tasks(self._mainloop):
                task.cancel()

        self._mainloop.call_soon_threadsafe(cancel_all_tasks)

        # Stop the webview
        if self._webview_worker is not None:
            self._webview_worker.request_stop()

    def try_load_app(self) -> rio.App:
        """
        Tries to load the user's app. If it fails, a dummy app is created and
        returned, unless running in release mode.
        """
        try:
            app = app_loading.load_user_app(self.proj)

        except app_loading.AppLoadError as err:
            # If running in release mode, no further attempts to load the app
            # will be made. This error is fatal.
            if not self.debug_mode:
                revel.fatal(f'The app could not be loaded: "{err}"')

            # Otherwise create a placeholder app which displays the error
            # message
            return app_loading.make_error_message_app(
                err,
                self.proj.project_directory,
                self._app_theme,
            )

        # Remember the app's theme. If in the future a placeholder app is used,
        # this theme will be used for it.
        self._app_theme = app._theme

        return app

    def run(self) -> None:
        assert not self._stop_requested.is_set()
        assert not self._server_is_ready.is_set()

        # Handle keyboard interrupts. KeyboardInterrupt exceptions are very
        # annoying to handle in async code, so instead we'll use a signal
        # handler.
        signal.signal(signal.SIGINT, lambda *_: self.stop(keyboard_interrupt=True))

        # Do as much work as possible in asyncio land
        asyncio_thread = threading.Thread(
            target=lambda: asyncio.run(
                self._run_async(),
            ),
            name="arbiter function of rio run",
        )
        asyncio_thread.start()

        # Wait for the http server to be ready
        self._server_is_ready.wait()

        # Make sure the startup was successful
        if self._stop_requested.is_set():
            return

        # The webview needs to be shown from the main thread. So, if running
        # inside of a window run the arbiter in a separate thread. Otherwise
        # just run it from this one.
        if self.run_in_window:
            self._webview_worker = webview_worker.WebViewWorker(
                push_event=self.push_event,
                debug_mode=self.debug_mode,
                url=self.url,
            )

            self._webview_worker.run()

        # If not running in a webview, just wait
        else:
            webbrowser.open(self.url)
            self._stop_requested.wait()

    async def _run_async(self) -> None:
        # Make sure the app is cleanly shut down, even if the arbiter crashes
        # for whichever reason.
        try:
            await self._run_async_inner()
        except BaseException:
            self.stop(keyboard_interrupt=False)

    async def _run_async_inner(self) -> None:
        # Print some initial messages
        print()
        print(f"[bold green]{LOGO_TEXT}[/]")
        print()
        print()
        print("Starting...")

        # Expose the mainloop
        self._mainloop = asyncio.get_running_loop()

        # Make sure the chosen port is available
        if not common.ensure_valid_port(self._host, self.port):
            error(f"The port [bold]{self.port}[/] is already in use.")
            print(f"Each port can only be used by one app at a time.")
            print(
                f"Try using another port, or let Rio choose one for you, by not specifying any port."
            )
            sys.exit(1)

        # Make sure the webview module is available
        if self.run_in_window and webview is None:
            fatal(
                "The `window` extra is required to run apps inside of a window."
                " Run `pip install rio-ui[[window]` to install it."
            )

        # If running in debug mode, install safeguards
        if self.debug_mode:
            apply_monkeypatches()

        # Try to load the app
        app = self.try_load_app()

        # Start the file watcher
        if self.debug_mode:
            self._file_watcher_worker = file_watcher_worker.FileWatcherWorker(
                push_event=self.push_event,
                proj=self.proj,
            )
            self._file_watcher_task = asyncio.create_task(
                self._file_watcher_worker.run(),
                name="File watcher",
            )

        # Start the uvicorn worker
        uvicorn_is_ready_event = asyncio.Event()

        self._uvicorn_worker = uvicorn_worker.UvicornWorker(
            push_event=self.push_event,
            app=app,
            port=self.port,
            host=self._host,
            quiet=self.quiet,
            debug_mode=self.debug_mode,
            run_in_window=self.run_in_window,
            on_server_is_ready=uvicorn_is_ready_event.set,
            on_startup_has_failed=lambda: self.stop(keyboard_interrupt=False),
        )

        self._uvicorn_task = asyncio.create_task(
            self._uvicorn_worker.run(),
            name="Uvicorn",
        )

        # Wait for the server to be ready
        revel.debug("Begin wait")
        await uvicorn_is_ready_event.wait()
        revel.debug("End wait")

        # Let everyone else know that the server is ready
        self._server_is_ready.set()

        # The app has just successfully started. Inform the user
        if self.debug_mode:
            warning("Rio is running in DEBUG mode.")
            warning(
                "Debug mode includes helpful tools for development, but is slower and disables some safety checks. Never use it in production!"
            )
            warning("Run with `--release` to disable debug mode.")
            print()

        if not self.run_in_window:
            revel.success(f"The app is running at [bold]{self.url}[/]")
            print()

        if self.public:
            warning(
                f"Running in [bold]public[/] mode. All devices on your network can access the app."
            )
            warning(f"Only run in public mode if you trust your network!")
            print()
        elif not self.run_in_window:
            print(
                f"[dim]Running in [/]local[dim] mode. Only this device can access the app.[/]"
            )
            print()

        # Keep track when the app was last reloaded
        last_reload_started_at = -1

        # Listen for events and react to them
        while True:
            event = await self._event_queue.get()

            # A file has changed
            if isinstance(event, run_models.FileChanged):
                # Ignore events that happened before the last reload started
                if event.timestamp_nanoseconds < last_reload_started_at:
                    continue

                # Display to the user that a reload is happening
                rel_path = event.path_to_file.relative_to(self.proj.project_directory)
                print()
                print(f"[bold]{rel_path}[/] has changed -> Reloading")

                # Restart the app
                await self._restart_app()

            # Somebody requested that the app should stop
            elif isinstance(event, run_models.StopRequested):
                self.stop(keyboard_interrupt=False)
                break

            # ???
            else:
                raise NotImplementedError(f'Unknown event "{event}"')

    def _spawn_traceback_popups(self, err: Union[str, BaseException]) -> None:
        """
        Displays a popup with the traceback in the rio UI.
        """
        popup_html = app_loading.make_traceback_html(
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

    async def _restart_app(self) -> None:
        assert self._uvicorn_worker is not None

        # Load the user's app again
        try:
            new_app = app_loading.load_user_app(self.proj)

        # If the app can't be loaded, create a placeholder app instead
        except app_loading.AppLoadError as err:
            new_app = app_loading.make_error_message_app(
                err,
                self.proj.project_directory,
                self._app_theme,
            )

            # Replace the app which is currently hosted by uvicorn
            self._uvicorn_worker.replace_app(new_app)

            # There is a subtlety here. Sessions which have requested their
            # index.html, but aren't yet connected to the websocket cannot
            # receive messages. So `_spawn_traceback_popups` will skip them.
            # This is fine as long as `self._app_server.app` has already been
            # assigned, since this ensures that any new websocket connections
            # will receive the new app anyway.
            #
            # -> This MUST happen after the new app has already been injected
            self._spawn_traceback_popups(err)

        else:
            # Replace the app which is currently hosted by uvicorn
            self._uvicorn_worker.replace_app(new_app)
            revel.success("Ready")

        # The app has changed, but the uvicorn server is still the same. Because
        # of this, uvicorn won't call the `on_app_start` function - do it
        # manually.
        app_server = self._uvicorn_worker.app_server
        await app_server._call_on_app_start()

        # Tell all sessions to reconnect, and close old sessions
        #
        # This can't use `self._evaluate_javascript`, it would race with closing
        # the sessions.
        for sess in list(app_server._active_session_tokens.values()):
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

    def _evaluate_javascript_in_all_sessions(self, javascript_source: str) -> None:
        """
        Runs the given javascript source in all connected sessions. Does not
        wait for or return the result.
        """
        assert self._uvicorn_worker is not None

        async def evaljs_as_coroutine(sess: rio.Session) -> None:
            await sess._evaluate_javascript(javascript_source)

        for sess in self._uvicorn_worker.app_server._active_session_tokens.values():
            asyncio.create_task(
                evaljs_as_coroutine(sess),
                name=f"Eval JS in session {sess._session_token}",
            )
