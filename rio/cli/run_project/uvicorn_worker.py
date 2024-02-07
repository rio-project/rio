import asyncio
import socket
from typing import *  # type: ignore

import revel
import uvicorn

import rio
import rio.app_server

from .. import nice_traceback
from . import run_models


class UvicornWorker:
    def __init__(
        self,
        *,
        push_event: Callable[[run_models.Event], None],
        app: rio.App,
        socket: socket.socket,
        quiet: bool,
        debug_mode: bool,
        run_in_window: bool,
        on_server_is_ready_or_failed: asyncio.Future[None],
    ) -> None:
        self.push_event = push_event
        self.app = app
        self.socket = socket
        self.quiet = quiet
        self.debug_mode = debug_mode
        self.run_in_window = run_in_window
        self.on_server_is_ready_or_failed = on_server_is_ready_or_failed

        # The app server used to host the app
        self.app_server: rio.app_server.AppServer | None = None

    async def run(self) -> None:
        # Set up a uvicorn server, but don't start it yet
        app_server = self.app._as_fastapi(
            debug_mode=self.debug_mode,
            running_in_window=self.run_in_window,
            validator_factory=None,
            internal_on_app_start=lambda: self.on_server_is_ready_or_failed.set_result(
                None
            ),
        )
        assert isinstance(app_server, rio.app_server.AppServer)
        self.app_server = app_server

        config = uvicorn.Config(
            self.app_server,
            log_level="error" if self.quiet else "info",
            timeout_graceful_shutdown=1,  # Without a timeout the server sometimes deadlocks
        )
        self._uvicorn_server = uvicorn.Server(config)

        # TODO: Univcorn wishes to set up the event loop. The current code
        # doesn't let it do that, since asyncio is already running.
        #
        # self._uvicorn_server.config.setup_event_loop()

        # Run the server
        try:
            await self._uvicorn_server.serve(
                sockets=[self.socket],
            )
        except Exception as err:
            revel.error(f"Uvicorn has crashed:")
            print()
            revel.print(nice_traceback.format_exception_revel(err))
            self.push_event(run_models.StopRequested())
        finally:
            self._uvicorn_server.should_exit = True

    def replace_app(self, app: rio.App) -> None:
        """
        Replace the app currently running in the server with a new one. The
        worker must already be running for this to work.
        """
        assert self.app_server is not None
        self.app_server.app = app
