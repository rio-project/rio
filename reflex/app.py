import functools
import io
import json
import secrets
import weakref
from datetime import timedelta
from typing import Callable, List, Optional

import fastapi
import PIL.Image
import timer_dict
import uniserde
import uvicorn

from . import assets, common, messages, session
from .common import Jsonable
from .widgets import widget_base

__all__ = [
    "App",
]


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
        build: Callable[[], widget_base.Widget],
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

        # The session tokens for all active sessions. These allow clients to
        # identify themselves, for example to reconnect in case of a lost
        # connection.
        self._active_session_tokens = timer_dict.TimerDict[str, None](
            default_duration=timedelta(minutes=60),
        )

        # All assets that have been registered with this session. They are held
        # weakly, meaning the session will host assets for as long as their
        # corresponding Python objects are alive.
        self._assets: weakref.WeakValueDictionary[
            str, assets.HostedAsset
        ] = weakref.WeakValueDictionary()

        # Fastapi
        self.api = fastapi.FastAPI()
        self.api.add_api_route("/", self._serve_index, methods=["GET"])
        self.api.add_api_route("/app.js.map", self._serve_js_map, methods=["GET"])
        self.api.add_api_route("/favicon.ico", self._serve_favicon, methods=["GET"])
        self.api.add_api_route("/asset/{asset_id}", self._serve_asset, methods=["GET"])
        self.api.add_api_websocket_route("/ws", self._serve_websocket)

    def run_as_website(self, *, quiet: bool = True) -> None:
        # Suppress stdout messages
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

    def weakly_host_asset(self, asset: assets.HostedAsset) -> None:
        """
        Register an asset with this session. The asset will be held weakly,
        meaning the session will host assets for as long as their corresponding
        Python objects are alive.
        """
        self._assets[asset.secret_id] = asset

    def check_and_refresh_session(self, session_token: str) -> None:
        """
        Look up the session token. If it is valid the session's duration
        is refreshed so it doesn't expire. If the token is not valid,
        a HttpException is raised.
        """

        if session_token not in self._active_session_tokens:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session token.",
            )

        self._active_session_tokens[session_token] = None

    def refresh_session(self, session_token: str) -> None:
        """
        Refresh the session's duration to prevent timeout.
        """
        self._active_session_tokens[session_token] = None

    async def _serve_index(self) -> fastapi.responses.HTMLResponse:
        """
        Handler for serving the index HTML page via fastapi.
        """
        # Create a new session token
        session_token = secrets.token_urlsafe()
        self._active_session_tokens[session_token] = None

        # Create a list of all messages the frontend should process immediately
        initial_messages: List[Jsonable] = [m.as_json() for m in []]

        # Load the templates
        html = read_frontend_template("index.html")
        js = read_frontend_template("app.js")
        css = read_frontend_template("style.css")

        # Fill in all placeholders
        js = js.replace("{session_token}", session_token)
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
        """
        Handler for serving the `app.js.map` file via fastapi.
        """
        return fastapi.responses.Response(
            content=read_frontend_template("app.js.map"),
            media_type="application/json",
        )

    async def _serve_favicon(self) -> fastapi.responses.Response:
        """
        Handler for serving the favicon via fastapi, if one is set.
        """
        if self.icon_as_ico_blob is None:
            return fastapi.responses.Response(status_code=404)

        return fastapi.responses.Response(
            content=self.icon_as_ico_blob,
            media_type="image/x-icon",
        )

    async def _serve_asset(self, asset_id: str) -> fastapi.responses.Response:
        """
        Handler for serving registered assets via fastapi. The app only
        references assets weakly, meaning trying to access an asset that has
        been garbage collected will result in a 404 error.
        """
        # Get the asset instance. The asset's id acts as a secret, so no further
        # authentication is required.
        try:
            asset = self._assets[asset_id]
        except KeyError:
            return fastapi.responses.Response(status_code=404)

        # Fetch the asset's content and respond
        if isinstance(asset.data, bytes):
            return fastapi.responses.Response(
                content=asset.data,
                media_type=asset.media_type,
            )
        else:
            return fastapi.responses.FileResponse(
                asset.data,
                media_type=asset.media_type,
            )

    async def _serve_websocket(
        self,
        websocket: fastapi.WebSocket,
        sessionToken: str,
    ):
        """
        Handler for establishing the websocket connection and handling any
        messages.
        """
        # Blah, naming conventions
        session_token = sessionToken
        del sessionToken

        # Make sure the session token is valid
        self.check_and_refresh_session(session_token)

        # Accept the socket
        await websocket.accept()

        # Create a session instance to hold all of this state in an organized
        # fashion
        root_widget = self.build()
        sess = session.Session(root_widget, websocket)

        # Trigger an initial build. This will also send the initial state to
        # the frontend.
        sess.register_dirty_widget(root_widget)
        await sess.refresh()

        while True:
            # Refresh the session's duration
            self._active_session_tokens[session_token] = None

            # Listen for incoming messages and react to them
            try:
                message_json = await websocket.receive_json()
                message = messages.IncomingMessage.from_json(message_json)

            # Don't spam when a client disconnects
            except fastapi.websockets.WebSocketDisconnect:
                return

            # Handle invalid JSON
            except (
                uniserde.SerdeError,
                json.JSONDecodeError,
                UnicodeDecodeError,
            ):
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                    detail="Received invalid JSON in websocket message",
                )

            # Delegate to the session
            await sess.handle_message(message)
