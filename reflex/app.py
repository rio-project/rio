from __future__ import annotations

import webbrowser
from typing import Awaitable, Callable, Optional

import fastapi
import PIL.Image
import uvicorn

from . import app_server, validator
from .widgets import widget_base

__all__ = [
    "App",
]


class App:
    def __init__(
        self,
        name: str,
        build: Callable[[], widget_base.Widget],
        *,
        icon: Optional[PIL.Image.Image] = None,
    ):
        self.name = name
        self.build = build
        self.icon = icon

    def as_fastapi(
        self,
        external_url: str,
        *,
        _validator_factory: Optional[Callable[[], validator.Validator]] = None,
    ) -> fastapi.FastAPI:
        return app_server.AppServer(
            self,
            external_url=external_url,
            validator_factory=_validator_factory,
        )

    def run_as_web_server(
        self,
        external_url: str,
        *,
        host: str = "localhost",
        port: int = 8000,
        quiet: bool = True,
        _validator_factory: Optional[Callable[[], validator.Validator]] = None,
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
        fastapi_server = self.as_fastapi(
            external_url=external_url,
            _validator_factory=_validator_factory,
        )

        # Register the startup event
        if _on_startup is not None:
            fastapi_server.add_event_handler("startup", _on_startup)

        # Serve
        uvicorn.run(
            fastapi_server,
            host=host,
            port=port,
            **kwargs,
        )

    def run_in_browser(
        self,
        *,
        external_url: Optional[str] = None,
        host: str = "localhost",
        port: int = 8000,
        quiet: bool = True,
        _validator_factory: Optional[Callable[[], validator.Validator]] = None,
    ):
        if external_url is None:
            external_url = f"http://{host}:{port}"

        async def on_startup(*args, **kwargs) -> None:
            webbrowser.open(external_url)

        self.run_as_web_server(
            external_url=external_url,
            host=host,
            port=port,
            quiet=quiet,
            _validator_factory=_validator_factory,
            _on_startup=on_startup,
        )
