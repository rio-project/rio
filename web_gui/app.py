import functools
import io
import json
import weakref
from typing import Callable, List, Optional

import fastapi
import PIL.Image
import uniserde
import uvicorn

from . import common, messages, session, widgets
from .common import Jsonable


@functools.lru_cache(maxsize=None)
def read_frontend_template(template_name: str) -> str:
    """
    Read a text file from the frontend directory and return its content. The
    results are cached to avoid repeated disk access.
    """
    return (common.FRONTEND_DIR / template_name).read_text()


class App:
    def __init__(
        self,
        name: str,
        build: Callable[[], widgets.Widget],
        *,
        host: str = "127.0.0.1",
        port: int = 8000,
        icon: Optional[PIL.Image.Image] = None,
    ):
        self.name = name
        self.build = build
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
        initial_messages: List[Jsonable] = [m.as_json() for m in []]

        # Load the templates
        html = read_frontend_template("index.html")
        js = read_frontend_template("app.js")
        css = read_frontend_template("style.css")

        # Fill in all placeholders
        js = js.replace(
            "'{initial_messages}'",
            json.dumps(initial_messages, indent=4),
        )

        html = html.replace("{title}", self.name)
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
            content=read_frontend_template("app.js.map"),
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
        # FIXME: Instead of reusing the root widget over and over, make sure
        #        each session gets a fresh, independent copy.

        # Accept the socket
        await websocket.accept()

        # Create a session instance to hold all of this state in an organized
        # fashion
        root_widget = self.build()
        sess = session.Session(root_widget)

        # Trigger an initial build
        sess.register_dirty_widget(root_widget)
        sess.refresh()

        # Building has spawned widgets. Send those to the client
        widget_json = sess._serialize_widget(root_widget)
        await websocket.send_json(messages.ReplaceWidgets(widget=widget_json).as_json())

        # Listen for incoming messages and react to them
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

            # Delegate to the session
            await sess.handle_message(message)
