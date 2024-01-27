import asyncio
import threading
from typing import *  # type: ignore

import revel
import uvicorn

import rio
import rio.app_server

from ... import common
from . import run_models


class UvicornWorker:
    def __init__(
        self,
        *,
        push_event: Callable[[run_models.Event], None],
        app: rio.App,
        host: str,
        port: int,
        quiet: bool,
        debug_mode: bool,
        run_in_window: bool,
        on_server_is_ready: Callable[[], None],
        on_startup_has_failed: Callable[[], None],
    ) -> None:
        self.push_event = push_event
        self.app = app
        self.host = host
        self.port = port
        self.quiet = quiet
        self.debug_mode = debug_mode
        self.on_server_is_ready = on_server_is_ready
        self.on_startup_has_failed = on_startup_has_failed

        # The app server used to host the app
        app_server = app._as_fastapi(
            debug_mode=self.debug_mode,
            running_in_window=run_in_window,
            validator_factory=None,
            internal_on_app_start=on_server_is_ready,
        )
        assert isinstance(app_server, rio.app_server.AppServer)
        self.app_server = app_server

    async def run(self) -> None:
        # Set up a uvicorn server, but don't start it yet
        config = uvicorn.Config(
            self.app_server,
            host=self.host,
            port=self.port,
            log_level="error" if self.quiet else "info",
            timeout_graceful_shutdown=1,  # Without a timeout the server sometimes deadlocks
        )
        self._uvicorn_server = uvicorn.Server(config)

        def run_uvicorn() -> None:
            assert self._uvicorn_server is not None

            try:
                revel.debug(f"Starting uvicorn on {self.host}:{self.port}")
                self._uvicorn_server.run()

            except BaseException:
                import traceback

                revel.error("UVICORN CRASHED:")
                traceback.print_exc()
                self.push_event(run_models.StopRequested())
                return

            else:
                revel.debug("Uviciron server has returned")

            # Nothing to do here. If the server stops running, it's because we
            # told it to - that means the program is already shutting down.

        print("Starting uvicorn thread")
        uvicorn_thread = threading.Thread(target=run_uvicorn)
        uvicorn_thread.start()

        try:
            # Wait until the task is canceled
            wait_forever_event = asyncio.Event()
            await wait_forever_event.wait()

        finally:
            self._uvicorn_server.should_exit = True

    def replace_app(self, app: rio.App) -> None:
        """
        Replace the app currently running in the server with a new one. The
        worker must already be running for this to work.
        """
        self.app_server.app = app
