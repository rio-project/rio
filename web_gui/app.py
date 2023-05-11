import functools
import io
import json
from datetime import timedelta
from typing import List, Optional

import fastapi
import PIL.Image
import uniserde
import uvicorn

from . import common, messages, widgets
from .common import Jsonable


@functools.lru_cache()
def read_template(template_name: str) -> str:
    return (common.FRONTEND_DIR / template_name).read_text()


class App:
    def __init__(
        self,
        app_name: str,
        root_widget: widgets.Widget,
        *,
        host: str = "127.0.0.1",
        port: int = 8000,
        icon: Optional[PIL.Image.Image] = None,
    ):
        self.app_name = app_name
        self.root_widget = root_widget
        self.host = host
        self.port = port

        if icon is None:
            self.icon_as_ico_blob = None
        else:
            icon_ico = io.BytesIO()
            icon.save(icon_ico, format="ICO")
            self.icon_as_ico_blob = icon_ico.getvalue()

        # Fastapi
        self.api = fastapi.FastAPI()
        self.api.add_api_route("/", self._serve_index, methods=["GET"])
        self.api.add_api_route("/app.js.map", self._serve_js_map, methods=["GET"])
        self.api.add_api_route("/favicon.ico", self._serve_favicon, methods=["GET"])
        self.api.add_api_websocket_route("/ws", self._serve_websocket)

    def run(self, *, quiet: bool = True) -> None:
        # Supress stdout messages
        kwargs = {}

        if quiet:
            kwargs["log_config"] = {
                "version": 1,
                "disable_existing_loggers": True,
                "formatters": {},
                "handlers": {},
                "loggers": {},
            }

        uvicorn.run(
            self.api,
            host=self.host,
            port=self.port,
            **kwargs,
        )

    async def _serve_index(self) -> fastapi.responses.HTMLResponse:
        # Create a list of all messages the frontend should process immediately
        widget_json = widgets._serialize(self.root_widget, type(self.root_widget))
        initial_messages: List[Jsonable] = [
            m.as_json()
            for m in [
                messages.ReplaceWidgets(widget=widget_json),
            ]
        ]

        # Load the templates
        html = read_template("index.html")
        js = read_template("app.js")
        css = read_template("style.css")

        # Fill in all placeholders
        js = js.replace(
            "'{initial_messages}'",
            json.dumps(initial_messages, indent=4),
        )

        html = html.replace("{title}", self.app_name)
        html = html.replace("/*{style}*/", css)
        html = html.replace("/*{script}*/", js)

        # DELETEME / TODO / FIXME
        #
        # Dump the html to a file for debugging
        out_dir = common.PACKAGE_ROOT_DIR.parent / "generated"
        out_dir.mkdir(exist_ok=True)
        (out_dir / "index.html").write_text(html)

        return fastapi.responses.HTMLResponse(html)

    async def _serve_js_map(self) -> fastapi.responses.Response:
        return fastapi.responses.Response(
            content=read_template("app.js.map"),
            media_type="application/json",
        )

    async def _serve_favicon(self) -> fastapi.responses.Response:
        if self.icon_as_ico_blob is None:
            return fastapi.responses.Response(status_code=404)

        return fastapi.responses.Response(
            content=self.icon_as_ico_blob,
            media_type="image/x-icon",
        )

    async def _serve_websocket(
        self,
        websocket: fastapi.WebSocket,
    ):
        await websocket.accept()

        while True:
            try:
                message_json = await websocket.receive_json()
                message = messages.IncomingMessage.from_json(message_json)
            except (
                uniserde.SerdeError,
                json.JSONDecodeError,
                UnicodeDecodeError,
            ) as err:
                # TODO what if invalid json is received
                raise NotImplementedError(err)

            print(message)
