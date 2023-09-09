from __future__ import annotations

import asyncio
import threading
import webbrowser
from datetime import timedelta
from typing import Optional, Callable, Awaitable, Any, Union, Iterable

import fastapi
import uvicorn

import reflex as rx

from . import app_server, assets, validator
from .common import ImageLike

# Only available with the `window` extra
try:
    import webview
except ImportError:
    webview = None


__all__ = ["App"]


class App:
    def __init__(
        self,
        name: str,
        build: Callable[[], rx.Widget],
        *,
        icon: Optional[ImageLike] = None,
        on_session_start: rx.EventHandler[rx.Session] = None,
        on_session_end: rx.EventHandler[rx.Session] = None,
        default_attachments: Iterable[Any] = (),
        ping_pong_interval: Union[int, float, timedelta] = timedelta(seconds=50),
    ):
        self.name = name
        self.build = build
        self._icon = None if icon is None else assets.Asset.from_image(icon)
        self.on_session_start = on_session_start
        self.on_session_end = on_session_end
        self.default_attachments = tuple(default_attachments)

        if isinstance(ping_pong_interval, timedelta):
            self.ping_pong_interval = ping_pong_interval
        else:
            self.ping_pong_interval = timedelta(seconds=ping_pong_interval)

    def as_fastapi(
        self,
        *,
        external_url_override: Optional[str] = None,
        _running_in_window: bool = False,
        _validator_factory: Optional[
            Callable[[rx.Session], validator.Validator]
        ] = None,
    ) -> fastapi.FastAPI:
        return app_server.AppServer(
            self,
            running_in_window=_running_in_window,
            external_url_override=external_url_override,
            on_session_start=self.on_session_start,
            on_session_end=self.on_session_end,
            default_attachments=self.default_attachments,
            validator_factory=_validator_factory,
        )

    def run_as_web_server(
        self,
        *,
        external_url_override: Optional[str] = None,
        host: str = "localhost",
        port: int = 8000,
        quiet: bool = True,
        _validator_factory: Optional[
            Callable[[rx.Session], validator.Validator]
        ] = None,
        _on_startup: Optional[Callable[[], Awaitable[None]]] = None,
    ) -> None:
        # Suppress stdout messages if requested
        kwargs = {}

        if quiet:
            kwargs["log_config"] = {
                "version": 1,
                "disable_existing_loggers": True,
                "formatters": {},
                "handlers": {},
                "loggers": {},
            }

        # Create the FastAPI server
        fastapi_app = self.as_fastapi(
            external_url_override=external_url_override,
            _running_in_window=False,
            _validator_factory=_validator_factory,
        )

        # Register the startup event
        if _on_startup is not None:
            fastapi_app.add_event_handler("startup", _on_startup)

        # Serve
        uvicorn.run(
            fastapi_app,
            host=host,
            port=port,
            **kwargs,
        )

    def run_in_browser(
        self,
        *,
        external_url_override: Optional[str] = None,
        host: str = "localhost",
        port: int = 8000,
        quiet: bool = True,
        _validator_factory: Optional[
            Callable[[rx.Session], validator.Validator]
        ] = None,
    ):
        async def on_startup() -> None:
            webbrowser.open(f"http://{host}:{port}")

        self.run_as_web_server(
            external_url_override=external_url_override,
            host=host,
            port=port,
            quiet=quiet,
            _validator_factory=_validator_factory,
            _on_startup=on_startup,
        )

    def run_in_window(
        self,
        quiet: bool = True,
        _validator_factory: Optional[
            Callable[[rx.Session], validator.Validator]
        ] = None,
    ):
        if webview is None:
            raise Exception(
                "The `window` extra is required to use `App.run_in_window`. Run `pip install reflex[window]` to install it."
            )

        # Unfortunately, WebView must run in the main thread, which makes this
        # tricky. We'll have to banish uvicorn to a background thread, and shut
        # it down when the window is closed.

        # TODO: How to choose a free port?
        host = "localhost"
        port = 8000
        url = f"http://{host}:{port}"

        # This lock is released once the server is running
        lock = threading.Lock()
        lock.acquire()

        server: Optional[uvicorn.Server] = None

        # Start the server, and release the lock once it's running
        def run_web_server():
            fastapi_app = self.as_fastapi(
                external_url_override=url,
                _running_in_window=True,
                _validator_factory=_validator_factory,
            )
            fastapi_app.add_event_handler("startup", lock.release)

            # Suppress stdout messages if requested
            kwargs = {}

            if quiet:
                kwargs["log_config"] = {
                    "version": 1,
                    "disable_existing_loggers": True,
                    "formatters": {},
                    "handlers": {},
                    "loggers": {},
                }

            nonlocal server
            config = uvicorn.Config(fastapi_app, host=host, port=port, **kwargs)
            server = uvicorn.Server(config)

            asyncio.run(server.serve())

        server_thread = threading.Thread(target=run_web_server)
        server_thread.start()

        # Wait for the server to start
        lock.acquire()

        # Start the webview
        try:
            webview.create_window(
                self.name,
                url,
            )
            webview.start()

        finally:
            assert server is not None

            server.should_exit = True
            server_thread.join()
