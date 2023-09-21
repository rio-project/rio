from __future__ import annotations

import asyncio
import os
import socket
import sys
import threading
import webbrowser
from datetime import timedelta
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterable, Optional, Union

import __main__
import fastapi
import uvicorn

import rio

from . import app_server, assets, debug
from .common import ImageLike

# Only available with the `window` extra
try:
    import webview  # type: ignore
except ImportError:
    webview = None


__all__ = ["App"]


class App:
    def __init__(
        self,
        build: Callable[[], rio.Widget],
        *,
        name: Optional[str] = None,
        icon: Optional[ImageLike] = None,
        on_session_start: rio.EventHandler[rio.Session] = None,
        on_session_end: rio.EventHandler[rio.Session] = None,
        default_attachments: Iterable[Any] = (),
        ping_pong_interval: Union[int, float, timedelta] = timedelta(seconds=50),
        assets_dir: Union[str, os.PathLike, None] = None,
    ):
        assert callable(
            build
        ), "The `build` argument must be a function that returns a Widget"

        main_file = _get_main_file()

        if name is None:
            name = _get_default_app_name(main_file)

        self.name = name
        self.build = build
        self._icon = None if icon is None else assets.Asset.from_image(icon)
        self.on_session_start = on_session_start
        self.on_session_end = on_session_end
        self.default_attachments = tuple(default_attachments)
        self.assets_dir = main_file.parent / (assets_dir or "")

        if isinstance(ping_pong_interval, timedelta):
            self.ping_pong_interval = ping_pong_interval
        else:
            self.ping_pong_interval = timedelta(seconds=ping_pong_interval)

    def _as_fastapi(
        self,
        *,
        external_url_override: Optional[str] = None,
        _running_in_window: bool = False,
        _validator_factory: Optional[Callable[[rio.Session], debug.Validator]] = None,
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

    def as_fastapi(
        self,
        *,
        external_url_override: Optional[str] = None,
        _validator_factory: Optional[Callable[[rio.Session], debug.Validator]] = None,
    ):
        return self._as_fastapi(
            external_url_override=external_url_override,
            _validator_factory=_validator_factory,
        )

    def run_as_web_server(
        self,
        *,
        external_url_override: Optional[str] = None,
        host: str = "localhost",
        port: int = 8000,
        quiet: bool = True,
        _validator_factory: Optional[Callable[[rio.Session], debug.Validator]] = None,
        _on_startup: Optional[Callable[[], Awaitable[None]]] = None,
    ) -> None:
        port = _ensure_valid_port(host, port)

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
        fastapi_app = self._as_fastapi(
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
        port: Optional[int] = None,
        quiet: bool = True,
        _validator_factory: Optional[Callable[[rio.Session], debug.Validator]] = None,
    ):
        port = _ensure_valid_port(host, port)

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
        _validator_factory: Optional[Callable[[rio.Session], debug.Validator]] = None,
    ):
        if webview is None:
            raise Exception(
                "The `window` extra is required to use `App.run_in_window`. Run `pip install rio[window]` to install it."
            )

        # Unfortunately, WebView must run in the main thread, which makes this
        # tricky. We'll have to banish uvicorn to a background thread, and shut
        # it down when the window is closed.

        host = "localhost"
        port = _ensure_valid_port(host, None)
        url = f"http://{host}:{port}"

        # This lock is released once the server is running
        lock = threading.Lock()
        lock.acquire()

        server: Optional[uvicorn.Server] = None

        # Start the server, and release the lock once it's running
        def run_web_server():
            fastapi_app = self._as_fastapi(
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


def _get_main_file() -> Path:
    try:
        return Path(__main__.__file__)
    except AttributeError:
        pass

    # Find out if we're being executed by uvicorn
    main_file = Path(sys.argv[0])
    if (
        main_file.name != "__main__.py"
        or main_file.parent != Path(uvicorn.__file__).parent
    ):
        return main_file

    # Find out from which module uvicorn imported the app
    try:
        app_location = next(arg for arg in sys.argv[1:] if ":" in arg)
    except StopIteration:
        return main_file

    module_name, _, _ = app_location.partition(":")
    module = sys.modules[module_name]

    if module.__file__ is None:
        return main_file

    return Path(module.__file__)


def _get_default_app_name(main_file: Path) -> str:
    name = main_file.stem
    if name in ("main", "__main__", "__init__"):
        name = main_file.absolute().parent.stem

    return name.replace("_", " ").title()


def _choose_free_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return sock.getsockname()[1]


def _port_is_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
            return False
        except OSError:
            return True


def _ensure_valid_port(host: str, port: Optional[int]) -> int:
    if port is None:
        return _choose_free_port(host)

    # if _port_is_in_use(host, port):
    #     raise ValueError(f"The port {host}:{port} is already in use")

    return port
