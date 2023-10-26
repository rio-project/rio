from __future__ import annotations

import asyncio
import contextlib
import copy
import functools
import inspect
import io
import json
import logging
import secrets
import time
import traceback
import weakref
from datetime import timedelta
from typing import *  # type: ignore

import babel
import fastapi
import pytz
import timer_dict
import uniserde.case_convert
from PIL import Image
from uniserde import Jsonable

import rio

from . import (
    app,
    assets,
    common,
    components,
    debug,
    global_state,
    inspection,
    routing,
    session,
    user_settings_module,
)
from .common import URL

try:
    import plotly
except ImportError:
    plotly = None

__all__ = ["AppServer"]


@functools.lru_cache(maxsize=None)
def read_frontend_template(template_name: str) -> str:
    """
    Read a text file from the frontend directory and return its content. The
    results are cached to avoid repeated disk access.
    """
    return (common.GENERATED_DIR / template_name).read_text(encoding="utf-8")


class InitialClientMessage(uniserde.Serde):
    website_url: str
    preferred_languages: List[str]
    timezone: str
    user_settings: Dict[str, Any]

    window_width: float
    window_height: float


async def _build_initial_messages(
    sess: session.Session, thm: rio.Theme
) -> List[Jsonable]:
    """
    Build the initial messages that are sent to the frontend when a new session
    is established.
    """
    # We'll temporarily replace the session's `send_message` method and make it
    # append all the messages to a list.
    initial_messages: List[Jsonable] = []

    async def send_message(msg: uniserde.Jsonable) -> None:
        initial_messages.append(msg)

    sess._send_message = send_message

    await sess._apply_theme(thm)

    # The methods we just called may have some side effects like registering
    # fonts. Registering fonts in particular is an operation that's done in a
    # background task, so we need to wait for that to finish.
    #
    # Since the session is freshly created, there shouldn't be any other tasks
    # running, so we can just wait for all of them.
    for task in sess._running_tasks:
        await task

    sess._send_message = session.dummy_send_message

    return initial_messages


async def _periodically_clean_up_expired_sessions(
    app_server_ref: weakref.ReferenceType[AppServer],
):
    LOOP_INTERVAL = 60 * 15
    SESSION_LIFETIME = 60 * 60

    while True:
        await asyncio.sleep(LOOP_INTERVAL)

        app_server = app_server_ref()
        if app_server is None:
            return

        now = time.monotonic()
        cutoff = now - SESSION_LIFETIME

        for session_token, session in list(app_server._active_session_tokens.items()):
            if session._last_interaction_timestamp < cutoff:
                del app_server._active_session_tokens[session_token]
                session._close()


class AppServer(fastapi.FastAPI):
    def __init__(
        self,
        app_: app.App,
        running_in_window: bool,
        on_session_start: rio.EventHandler[rio.Session],
        on_session_end: rio.EventHandler[rio.Session],
        default_attachments: Tuple[Any, ...],
        validator_factory: Optional[Callable[[rio.Session], debug.Validator]],
        internal_on_app_start: Optional[Callable[[], None]],
    ):
        super().__init__(lifespan=__class__._lifespan)

        self.app = app_
        self.running_in_window = running_in_window
        self.on_session_start = on_session_start
        self.on_session_end = on_session_end
        self.default_attachments = default_attachments
        self.validator_factory = validator_factory
        self.internal_on_app_start = internal_on_app_start

        # Initialized lazily, when the favicon is first requested.
        self._icon_as_ico_blob: Optional[bytes] = None

        # The session tokens for all active sessions. These allow clients to
        # identify themselves, for example to reconnect in case of a lost
        # connection.
        self._active_session_tokens: Dict[str, rio.Session] = {}

        # All assets that have been registered with this session. They are held
        # weakly, meaning the session will host assets for as long as their
        # corresponding Python objects are alive.
        #
        # Assets registered here are hosted under `/asset/temp-{asset_id}`. In
        # addition the server also permanently hosts other "well known" assets
        # (such as javascript dependencies) which are available under public
        # URLS at `/asset/{some-name}`.
        self._assets: weakref.WeakValueDictionary[
            str, assets.Asset
        ] = weakref.WeakValueDictionary()

        # All pending file uploads. These are stored in memory for a limited
        # time. When a file is uploaded the corresponding future is set.
        self._pending_file_uploads: timer_dict.TimerDict[
            str, asyncio.Future[List[common.FileInfo]]
        ] = timer_dict.TimerDict(default_duration=timedelta(minutes=15))

        # FastAPI

        # self.add_api_route("/app.js.map", self._serve_js_map, methods=["GET"])
        # self.add_api_route("/style.css.map", self._serve_css_map, methods=["GET"])
        self.add_api_route("/rio/favicon.ico", self._serve_favicon, methods=["GET"])
        self.add_api_route(
            "/rio/asset/{asset_id:path}", self._serve_asset, methods=["GET"]
        )
        self.add_api_route(
            "/rio/upload/{upload_token}", self._serve_file_upload, methods=["PUT"]
        )
        self.add_api_websocket_route("/rio/ws", self._serve_websocket)

        # Because this is a single page application, all other routes should
        # serve the index page. The session will determine which components should
        # be shown.
        self.add_api_route(
            "/{initial_route_str:path}", self._serve_index, methods=["GET"]
        )

    @contextlib.asynccontextmanager
    async def _lifespan(self):
        # If running as a server, periodically clean up expired sessions
        if not self.running_in_window:
            assert type(self) is AppServer  # Shut up pyright

            asyncio.create_task(
                _periodically_clean_up_expired_sessions(weakref.ref(self)),
                name="Periodic session cleanup",
            )

        # Trigger the app's startup event
        #
        # This will be done blockingly, so the user can prepare any state before
        # connections are accepted. This is also why it's called before the
        # internal event.
        if self.app._on_app_start is not None:
            try:
                result = self.app._on_app_start(self.app)

                if inspect.isawaitable(result):
                    await result

            # Display and discard exceptions
            except Exception:
                print("Exception in `on_app_start` event handler:")
                traceback.print_exc()

        # Trigger any internal startup event
        if self.internal_on_app_start is not None:
            self.internal_on_app_start()

        yield

    def weakly_host_asset(self, asset: assets.HostedAsset) -> None:
        """
        Register an asset with this server. The asset will be held weakly,
        meaning the server will host assets for as long as their corresponding
        Python objects are alive.

        If another asset with the same id is already hosted, it will be
        replaced.
        """
        self._assets[asset.secret_id] = asset

    def host_asset_with_timeout(self, asset: assets.HostedAsset, timeout: float) -> URL:
        """
        Hosts an asset for a limited time. Returns the asset's url.
        """
        self.weakly_host_asset(asset)

        async def keep_alive():
            await asyncio.sleep(timeout)
            _ = asset

        asyncio.create_task(
            keep_alive(), name=f"Keep asset {asset} alive for {timeout} sec"
        )

        return asset.url

    async def _serve_index(
        self,
        request: fastapi.Request,
        initial_route_str: str,
    ) -> fastapi.responses.HTMLResponse:
        """
        Handler for serving the index HTML page via fastapi.
        """

        # Because Rio apps are single-page, this route serves as the fallback.
        # In addition to legitimate requests for HTML pages, it will also catch
        # a bunch of invalid requests to other resources. To highlight this,
        # throw a 404 if HTML is not explicitly requested.
        #
        # Currently inactive, because this caused issues behind dumb proxies
        # that don't pass on the `accept` header.

        # if not request.headers.get("accept", "").startswith("text/html"):
        #     raise fastapi.HTTPException(
        #         status_code=fastapi.status.HTTP_404_NOT_FOUND,
        #     )

        # Prepare some URL constants
        base_url = rio.URL(str(request.base_url))
        assert base_url.is_absolute(), base_url

        initial_page_url_absolute = rio.URL(str(request.url))
        assert initial_page_url_absolute.is_absolute(), initial_page_url_absolute

        initial_page_url_relative = common.make_url_relative(
            base_url,
            initial_page_url_absolute,
        )

        # Create a session instance to hold all of this state in an organized
        # fashion.
        #
        # The session is still missing a lot of values at this point, such as
        # `send_message` and `receive_message`. It will be finished once the
        # websocket connection is established.
        session_token = secrets.token_urlsafe()

        sess = session.Session(
            app_server_=self,
            base_url=rio.URL(str(request.base_url)),
            initial_page=initial_page_url_absolute,
        )

        self._active_session_tokens[session_token] = sess

        # Run any page guards for the initial page
        try:
            (
                initial_page_instances,
                initial_page_url_absolute,
            ) = routing.check_page_guards(
                sess,
                target_url_relative=initial_page_url_relative,
                target_url_absolute=initial_page_url_absolute,
            )
        except routing.NavigationFailed:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Navigation to initial page "{initial_page_url_absolute}" has failed.',
            ) from None

        # Update the session's active page
        sess._active_page_url = initial_page_url_absolute
        sess._active_page_instances = tuple(initial_page_instances)

        # Add any attachments, except for user settings. These are deserialized
        # later on, once the client has sent the initial message.
        for attachment in self.default_attachments:
            if isinstance(attachment, user_settings_module.UserSettings):
                continue

            sess.attachments.add(copy.deepcopy(attachment))

        # Make sure a theme is attached
        if rio.Theme in sess.attachments:
            thm = sess.attachments[rio.Theme]
        else:
            thm = rio.Theme.from_color()
            sess.attachments.add(thm)

        # Create a list of initial messages for the client to process
        initial_messages = await _build_initial_messages(sess, thm)

        # Load the templates
        html = read_frontend_template("index.html")

        # Fill in any placeholders
        html = html.replace(
            "{session_token}",
            session_token,
        )

        html = html.replace(
            '"{child_attribute_names}"',
            json.dumps(
                inspection.get_child_component_containing_attribute_names_for_builtin_components()
            ),
        )

        html = html.replace(
            '"{initial_messages}"',
            json.dumps(initial_messages),
        )

        html = html.replace(
            '"{ping_pong_interval}"',
            str(self.app._ping_pong_interval.total_seconds()),
        )

        # Merge everything into one HTML
        html = html.replace("{title}", self.app.name)

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
                icon_blob, _ = await self.app._icon.try_fetch_as_blob()

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
        `/asset/{some-name}` path.

        In addition, `HostedAsset` instances are hosted under their secret id
        under the `/asset/temp-{asset_id}` path. These assets are held weakly
        by the session, meaning they will be served for as long as the
        corresponding Python object is alive.
        """

        # Special case: plotly
        #
        # The python plotly library already includes a minified version of
        # plotly.js. Rather than shipping another one, just serve the one
        # included in the library.
        if asset_id == "plotly.min.js" and plotly is not None:
            return fastapi.responses.Response(
                content=plotly.offline.get_plotlyjs(),
                media_type="text/javascript",
            )

        # Well known asset?
        if not asset_id.startswith("temp-"):
            # Construct the path to the target file
            asset_file_path = common.HOSTED_ASSETS_DIR / asset_id

            # Make sure the path is inside the hosted assets directory
            #
            # TODO: Is this safe? Would this allow the client to break out from
            # the directory using tricks such as "../", links, etc?
            asset_file_path = asset_file_path.resolve()
            if common.HOSTED_ASSETS_DIR not in asset_file_path.parents:
                logging.warning(
                    f'Client requested asset "{asset_id}" which is not located inside the hosted assets directory. Somebody might be trying to break out of the assets directory!'
                )
                return fastapi.responses.Response(status_code=404)

            # TODO: Can this check be avoided? `FileResponse` may already be
            # doing it internally anyway.
            if asset_file_path.exists():
                return fastapi.responses.FileResponse(
                    common.HOSTED_ASSETS_DIR / asset_id,
                )

            # No such file
            return fastapi.responses.Response(status_code=404)

        # Get the asset's Python instance. The asset's id acts as a secret, so
        # no further authentication is required.
        try:
            asset = self._assets[asset_id.removeprefix("temp-")]
        except KeyError:
            return fastapi.responses.Response(status_code=404)

        # Fetch the asset's content and respond
        if isinstance(asset, assets.BytesAsset):
            return fastapi.responses.Response(
                content=asset.data,
                media_type=asset.media_type,
            )
        elif isinstance(asset, assets.PathAsset):
            return fastapi.responses.FileResponse(
                asset.path,
                media_type=asset.media_type,
            )
        else:
            assert False, f"Unable to serve asset of unknown type: {asset}"

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
        parsed_file_sizes: List[int] = []
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

        # Accept the socket
        await websocket.accept()

        # Look up the session token. If it is valid the session's duration is
        # refreshed so it doesn't expire. If the token is not valid, don't
        # accept the websocket.
        try:
            sess = self._active_session_tokens[session_token]
        except KeyError:
            # Inform the client that it's session token is unknown and request a
            # refresh
            await websocket.send_json(
                {
                    "jsonrpc": "2.0",
                    "method": "invalidSessionToken",
                    "params": {},
                }
            )

            await websocket.close(
                3000,  # Custom error code
                "Invalid session token.",
            )
            return

        # Optionally create a validator
        validator_instance = (
            None if self.validator_factory is None else self.validator_factory(sess)
        )

        # Create a function for sending messages to the frontend. This function
        # will also pipe the message to the validator if one is present.
        if self.validator_factory is None:

            async def receive_message() -> uniserde.Jsonable:
                # Refresh the session's duration
                self._active_session_tokens[session_token] = sess

                # Fetch a message
                return await websocket.receive_json()

            sess._send_message = websocket.send_json  # type: ignore
            sess._receive_message = receive_message

        else:

            async def send_message(msg: uniserde.Jsonable) -> None:
                assert isinstance(validator_instance, debug.Validator)
                validator_instance.handle_outgoing_message(msg)
                await websocket.send_json(msg)

            async def receive_message() -> uniserde.Jsonable:
                assert isinstance(validator_instance, debug.Validator)
                # Refresh the session's duration
                self._active_session_tokens[session_token] = sess

                # Fetch a message
                msg = await websocket.receive_json()
                validator_instance.handle_incoming_message(msg)
                return msg

            sess._send_message = send_message
            sess._receive_message = receive_message

        # Check if this is a reconnect
        if hasattr(sess, "window_width"):
            init_coro = sess._send_reconnect_message()
        else:
            await self._finish_session_initialization(sess, websocket, session_token)

            # Trigger a refresh. This will also send the initial state to the
            # frontend.
            init_coro = sess._refresh()

        try:
            # This is done in a task because the server is not yet running, so
            # the method would never receive a response, and thus would hang
            # indefinitely.
            sess.create_task(init_coro, name=f"Session {sess} init")

            # Serve the socket
            await sess.serve()

        # Don't spam the terminal just because a client disconnected
        except fastapi.WebSocketDisconnect:
            pass

        finally:
            # Fire the session end event
            await sess._call_event_handler(self.on_session_end, sess)

    async def _finish_session_initialization(
        self,
        sess: session.Session,
        websocket: fastapi.WebSocket,
        session_token: str,
    ) -> None:
        # Upon connecting, the client sends an initial message containing
        # information about it. Wait for that, but with a timeout - otherwise
        # evildoers could overload the server with connections that never send
        # anything.
        initial_message_json: Jsonable = await asyncio.wait_for(
            websocket.receive_json(),
            timeout=60,
        )
        initial_message = InitialClientMessage.from_json(initial_message_json)  # type: ignore

        sess.window_width = initial_message.window_width
        sess.window_height = initial_message.window_height

        # Parse the preferred locales
        preferred_locales: List[babel.Locale] = []

        for raw_locale_string in initial_message.preferred_languages:
            try:
                preferred_locales.append(
                    babel.Locale.parse(
                        raw_locale_string.replace("-", "_"),
                    )
                )
            except ValueError:
                pass

        if not preferred_locales:
            preferred_locales.append(babel.Locale.parse("en"))

        sess.preferred_locales = tuple(preferred_locales)

        # Parse the timezone
        try:
            sess.timezone = pytz.timezone(initial_message.timezone)
        except pytz.UnknownTimeZoneError:
            logging.warning(
                f'Client sent unknown timezone "{initial_message.timezone}". Using UTC instead.'
            )
            sess.timezone = pytz.UTC

        # Publish the external URL via the session
        sess.external_url = (
            None if self.running_in_window else initial_message.website_url
        )

        # Deserialize the user settings
        await sess._load_user_settings(initial_message.user_settings)

        # Create the root component. The root component is a non-fundamental component,
        # because that has many advantages:
        # 1. Every component except for the root component itself has a valid builder
        # 2. The JS code is simpler because the root component can't have an
        #    alignment or margin
        # 3. Children of non-fundamental components are automatically initialized
        #    correctly, so we don't need to duplicate that logic here
        global_state.currently_building_component = None
        global_state.currently_building_session = sess

        try:
            sess._root_component = RootContainer(self.app._build)
        finally:
            global_state.currently_building_session = None

        # Trigger the `on_session_start` event.
        #
        # Note: Since this event is often used for initialization, like adding
        # attachments, we actually wait for it to finish before continuing.
        await sess._call_event_handler(self.on_session_start, sess)


class RootContainer(components.Component):
    build_function: Callable[[], components.Component]

    def build(self) -> rio.Component:
        return self.build_function()
