from __future__ import annotations

import asyncio
import functools
import io
import json
import secrets
import traceback
import weakref
from datetime import timedelta
from pathlib import Path
from typing import *  # type: ignore

import fastapi
import plotly
import timer_dict
import uniserde
from PIL import Image

import reflex as rx
import reflex.widgets.metadata

from . import app, assets, common, messages, session, validator
from .common import Jsonable

__all__ = [
    "AppServer",
]

CHILD_ATTRIBUTE_NAMES_JSON = json.dumps(
    {
        unique_id: list(attribute_names)
        for unique_id, attribute_names in reflex.widgets.metadata.CHILD_ATTRIBUTE_NAMES.items()
    }
)


@functools.lru_cache(maxsize=None)
def read_frontend_template(template_name: str) -> str:
    """
    Read a text file from the frontend directory and return its content. The
    results are cached to avoid repeated disk access.
    """
    return (common.GENERATED_DIR / template_name).read_text(encoding="utf-8")


class AppServer(fastapi.FastAPI):
    def __init__(
        self,
        app_: app.App,
        external_url: str,
        on_session_started: rx.EventHandler[rx.Session],
        validator_factory: Optional[Callable[[rx.Session], validator.Validator]],
    ):
        super().__init__()

        # TODO: Maybe parse the url and remove the backslash? Document this?
        # Something?
        assert not external_url.endswith("/"), external_url

        self.app = app_
        self.external_url = external_url
        self.on_session_started = on_session_started
        self.validator_factory = validator_factory

        # Initialized lazily, when the favicon is first requested.
        self._icon_as_ico_blob: Optional[bytes] = None

        # The session tokens for all active sessions. These allow clients to
        # identify themselves, for example to reconnect in case of a lost
        # connection.
        self._active_session_tokens = timer_dict.TimerDict[str, None](
            default_duration=timedelta(minutes=60),
        )

        # All assets that have been registered with this session. They are held
        # weakly, meaning the session will host assets for as long as their
        # corresponding Python objects are alive.
        #
        # Assets registered here are hosted under `/asset/temp-{asset_id}`. In
        # addition the server also hosts other assets (such as javascript
        # dependencies) which are available under public URLS at
        # `/asset/{some-name}`.
        self._assets: weakref.WeakValueDictionary[
            str, assets.HostedAsset
        ] = weakref.WeakValueDictionary()

        # All pending file uploads. These are stored in memory for a limited
        # time. When a file is uploaded the corresponding future is set.
        self._pending_file_uploads: timer_dict.TimerDict[
            str, asyncio.Future[List[common.FileInfo]]
        ] = timer_dict.TimerDict(default_duration=timedelta(minutes=15))

        # Fastapi
        self.add_api_route("/", self._serve_index, methods=["GET"])
        # self.add_api_route("/app.js.map", self._serve_js_map, methods=["GET"])
        # self.add_api_route("/style.css.map", self._serve_css_map, methods=["GET"])
        self.add_api_route("/reflex/favicon.ico", self._serve_favicon, methods=["GET"])
        self.add_api_route(
            "/reflex/asset/{asset_id}", self._serve_asset, methods=["GET"]
        )
        self.add_api_route(
            "/reflex/upload/{upload_token}", self._serve_file_upload, methods=["PUT"]
        )
        self.add_api_websocket_route("/reflex/ws", self._serve_websocket)

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
            '"{initial_messages}"',
            json.dumps(initial_messages, indent=4),
        )
        js = js.replace('"{child_attribute_names}"', CHILD_ATTRIBUTE_NAMES_JSON)

        html = html.replace("{title}", self.app.name)
        html = html.replace("/*{style}*/", css)
        html = html.replace("/*{script}*/", js)

        # Respond
        return fastapi.responses.HTMLResponse(html)

    async def _serve_js_map(self) -> fastapi.responses.Response:
        """
        Handler for serving the `app.js.map` file via fastapi.
        """
        return fastapi.responses.Response(
            content=read_frontend_template("app.js.map"),
            media_type="application/json",
        )

    async def _serve_css_map(self) -> fastapi.responses.Response:
        """
        Handler for serving the `style.css.map` file via fastapi.
        """
        return fastapi.responses.Response(
            content=read_frontend_template("style.css.map"),
            media_type="application/json",
        )

    async def _serve_favicon(self) -> fastapi.responses.Response:
        """
        Handler for serving the favicon via fastapi, if one is set.
        """
        # If an icon is set, make sure a cached version exists
        if self._icon_as_ico_blob is None and self.app._icon is not None:
            try:
                icon_blob, _ = await self.app._icon._try_fetch_as_blob()

                input_buffer = io.BytesIO(icon_blob)
                output_buffer = io.BytesIO()

                with Image.open(input_buffer) as image:
                    image.save(output_buffer, format="ico")

            except Exception as err:
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not fetch the app's icon.",
                ) from err

            self._icon_as_ico_blob = output_buffer.getvalue()

        # No icon set or fetching failed
        if self._icon_as_ico_blob is None:
            return fastapi.responses.Response(status_code=404)

        # There is an icon, respond
        return fastapi.responses.Response(
            content=self._icon_as_ico_blob,
            media_type="image/x-icon",
        )

    async def _serve_asset(self, asset_id: str) -> fastapi.responses.Response:
        """
        Handler for serving assets via fastapi.

        Some common assets are hosted under permanent, well known URLs under the
        `/assets/{some-name}` path.

        In addition, `HostedAsset` instances are hosted under their secret id
        under the `/assets/temp-{asset_id}` path. These assets are held weakly
        by the session, meaning they will be served for as long as the
        corresponding Python object is alive.
        """

        # Special case: plotly
        #
        # The python plotly library already includes a minified version of
        # plotly.js. Rather than shipping another one, just serve the one
        # included in the library.
        if asset_id == "plotly.min.js":
            return fastapi.responses.Response(
                content=plotly.offline.get_plotlyjs(),
                media_type="text/javascript",
            )

        # Well known asset?
        if not asset_id.startswith("temp-"):
            # TODO: Is this safe? Would this allow the client to break out
            # from the directory using names such as `../`?
            asset_file_path = common.HOSTED_ASSETS_DIR / asset_id

            # TODO: Can this check be avoided?
            if asset_file_path.exists():
                return fastapi.responses.FileResponse(
                    common.HOSTED_ASSETS_DIR / asset_id
                )

            return fastapi.responses.Response(status_code=404)

        # Get the asset's Python instance. The asset's id acts as a secret, so
        # no further authentication is required.
        try:
            asset = self._assets[asset_id.removeprefix("temp-")]
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

    async def _serve_file_upload(
        self,
        upload_token: str,
        file_names: List[str],
        file_types: List[str],
        file_sizes: List[str],
        # If no files are uploaded `files` isn't present in the form data at
        # all. Using a default value ensures that those requests don't fail
        # because of "missing parameters".
        #
        # Lists are mutable, make sure not to modify this value!
        file_streams: List[fastapi.UploadFile] = [],
    ):
        # Try to find the future for this token
        try:
            future = self._pending_file_uploads.pop(upload_token)
        except KeyError:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail="Invalid upload token.",
            )

        # Make sure the same number of values was received for each parameter
        n_names = len(file_names)
        n_types = len(file_types)
        n_sizes = len(file_sizes)
        n_streams = len(file_streams)

        if n_names != n_types or n_names != n_sizes or n_names != n_streams:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Inconsistent number of files between the different message parts.",
            )

        # Parse the file sizes
        parsed_file_sizes = []
        for file_size in file_sizes:
            try:
                parsed = int(file_size)
            except ValueError:
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid file size.",
                )

            if parsed < 0:
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid file size.",
                )

            parsed_file_sizes.append(parsed)

        # Complete the future
        future.set_result(
            [
                common.FileInfo(
                    name=file_names[ii],
                    size_in_bytes=parsed_file_sizes[ii],
                    media_type=file_types[ii],
                    _contents=await file_streams[ii].read(),
                )
                for ii in range(n_names)
            ]
        )

        return fastapi.responses.Response(status_code=fastapi.status.HTTP_200_OK)

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

        # Create a function for sending messages to the frontend. This function
        # will also pipe the message to the validator if one is present.
        async def send_message(
            msg: messages.OutgoingMessage,
        ) -> None:
            nonlocal validator

            if validator is not None:
                validator.handle_outgoing_message(msg)

            await websocket.send_json(msg.as_json())

        # Create a session instance to hold all of this state in an organized
        # fashion
        root_widget = self.app.build()
        sess = session.Session(
            root_widget,
            send_message,
            self,
        )

        # Optionally create a validator
        validator = (
            None if self.validator_factory is None else self.validator_factory(sess)
        )

        # Trigger the `on_session_started` event
        await common.call_event_handler(self.on_session_started, sess)

        # Trigger an initial build. This will also send the initial state to
        # the frontend.
        sess._register_dirty_widget(
            root_widget, include_fundamental_children_recursively=True
        )
        await sess._refresh()

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
                traceback.print_exc()
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                    detail="Received invalid JSON in websocket message",
                )

            # Invoke the validator if one is present
            if validator is not None:
                validator.handle_incoming_message(message)

            # Delegate to the session
            await sess._handle_message(message)
