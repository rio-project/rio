from __future__ import annotations

import asyncio
import copy
import functools
import io
import json
import logging
import secrets
import weakref
from datetime import timedelta
from typing import *  # type: ignore

import babel
import fastapi
import timer_dict
import uniserde.case_convert
import yarl
from PIL import Image
from uniserde import Jsonable

import reflex as rx

from . import (
    app,
    assets,
    common,
    debug,
    global_state,
    inspection,
    session,
    user_settings_module,
)

try:
    import plotly  # type: ignore
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
    user_settings: Dict[str, Any]

    window_width: float
    window_height: float


def _build_set_theme_variables_message(thm: rx.Theme):
    """
    Build a message which, when sent to the client, sets the root element's CSS
    theme variables.

    The result is a valid JSON-RPC message, without an ID set (so don't expect a
    response).
    """

    # Build the set of all variables

    # Miscellaneous
    variables: Dict[str, str] = {
        "--reflex-global-corner-radius-small": f"{thm.corner_radius_small}rem",
        "--reflex-global-corner-radius-large": f"{thm.corner_radius_large}rem",
        "--reflex-global-shadow-radius": f"{thm.shadow_radius}rem",
    }

    # Theme Colors
    color_names = (
        "primary_color",
        "secondary_color",
        "disabled_color",
        "primary_color_variant",
        "secondary_color_variant",
        "disabled_color_variant",
        "background_color",
        "surface_color",
        "surface_color_variant",
        "surface_active_color",
        "success_color",
        "warning_color",
        "danger_color",
        "success_color_variant",
        "warning_color_variant",
        "danger_color_variant",
        "shadow_color",
        "heading_on_primary_color",
        "text_on_primary_color",
        "heading_on_secondary_color",
        "text_on_secondary_color",
        "text_color_on_light",
        "text_color_on_dark",
    )

    for py_color_name in color_names:
        css_color_name = f'--reflex-global-{py_color_name.replace("_", "-")}'
        color = getattr(thm, py_color_name)
        assert isinstance(color, rx.Color), color
        variables[css_color_name] = f"#{color.hex}"

    # Text styles
    style_names = (
        "heading1",
        "heading2",
        "heading3",
        "text",
    )

    for style_name in style_names:
        style = getattr(thm, f"{style_name}_style")
        assert isinstance(style, rx.TextStyle), style

        css_prefix = f"--reflex-global-{style_name}"
        variables[f"{css_prefix}-font-name"] = style.font_name
        variables[f"{css_prefix}-color"] = f"#{style.font_color.hex}"
        variables[f"{css_prefix}-font-size"] = f"{style.font_size}rem"
        variables[f"{css_prefix}-italic"] = "italic" if style.italic else "normal"
        variables[f"{css_prefix}-font-weight"] = style.font_weight
        variables[f"{css_prefix}-underlined"] = (
            "underline" if style.underlined else "unset"
        )
        variables[f"{css_prefix}-all-caps"] = "uppercase" if style.all_caps else "unset"

    # Colors that need to be extracted from styles
    variables[
        "--reflex-global-heading-on-surface-color"
    ] = f"#{thm.heading1_style.font_color.hex}"

    variables[
        "--reflex-global-text-on-surface-color"
    ] = f"#{thm.text_style.font_color.hex}"

    # Colors derived from, but not stored in the theme
    derived_colors = {
        "text-on-success-color": thm.text_color_for(thm.success_color),
        "text-on-warning-color": thm.text_color_for(thm.warning_color),
        "text-on-danger-color": thm.text_color_for(thm.danger_color),
    }

    for css_name, color in derived_colors.items():
        variables[f"--reflex-global-{css_name}"] = f"#{color.hex}"

    # Assign to the html's `data-theme` attribute. This is used to dynamically
    # switch highlight.js themes.
    theme_variant = (
        "light" if thm.background_color.perceived_brightness > 0.5 else "dark"
    )

    # Build JavaScript code which applies the theme
    js_source = f"""
VARIABLES = {json.dumps(variables)};

// Expose the CSS Variables
for (let key in VARIABLES) {{
    document.documentElement.style.setProperty(
        key,
        VARIABLES[key]
    );
}}
response = null;

// Set the theme variant
document.documentElement.setAttribute("data-theme", "{theme_variant}");
"""

    # Wrap in JSON-RPC
    return {
        "jsonrpc": "2.0",
        "method": "evaluateJavaScript",
        "params": {
            "javaScriptSource": js_source,
        },
    }


class AppServer(fastapi.FastAPI):
    def __init__(
        self,
        app_: app.App,
        running_in_window: bool,
        external_url_override: Optional[str],
        on_session_start: rx.EventHandler[rx.Session],
        on_session_end: rx.EventHandler[rx.Session],
        default_attachments: Tuple[Any, ...],
        validator_factory: Optional[Callable[[rx.Session], debug.Validator]],
    ):
        super().__init__()

        # TODO: Maybe parse the url and remove the backslash? Document this?
        # Something?
        assert external_url_override is None or not external_url_override.endswith(
            "/"
        ), external_url_override

        self.app = app_
        self.running_in_window = running_in_window
        self.external_url_override = external_url_override
        self.on_session_start = on_session_start
        self.on_session_end = on_session_end
        self.default_attachments = default_attachments
        self.validator_factory = validator_factory

        # Initialized lazily, when the favicon is first requested.
        self._icon_as_ico_blob: Optional[bytes] = None

        # The session tokens for all active sessions. These allow clients to
        # identify themselves, for example to reconnect in case of a lost
        # connection.
        self._active_session_tokens = timer_dict.TimerDict[str, rx.Session](
            default_duration=timedelta(minutes=9999999 if running_in_window else 60),
        )

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

        # Fastapi
        # self.add_api_route("/app.js.map", self._serve_js_map, methods=["GET"])
        # self.add_api_route("/style.css.map", self._serve_css_map, methods=["GET"])
        self.add_api_route("/reflex/favicon.ico", self._serve_favicon, methods=["GET"])
        self.add_api_route(
            "/reflex/asset/{asset_id:path}", self._serve_asset, methods=["GET"]
        )
        self.add_api_route(
            "/reflex/upload/{upload_token}", self._serve_file_upload, methods=["PUT"]
        )
        self.add_api_websocket_route("/reflex/ws", self._serve_websocket)

        # Because this is a single page application, all other routes should
        # serve the index page. The session will determine which widgets should
        # be shown.
        self.add_api_route(
            "/{initial_route_str:path}", self._serve_index, methods=["GET"]
        )

    def weakly_host_asset(self, asset: assets.HostedAsset) -> None:
        """
        Register an asset with this session. The asset will be held weakly,
        meaning the session will host assets for as long as their corresponding
        Python objects are alive.

        If another asset with the same id is already hosted, it will be
        replaced.
        """
        # FIXME: This is unsafe. What if first a long lived instance is
        # assigned, then overwritten by a short-lived one?
        self._assets[asset.secret_id] = asset

    def check_and_refresh_session(self, session_token: str) -> rx.Session:
        """
        Look up the session token. If it is valid the session's duration
        is refreshed so it doesn't expire. If the token is not valid,
        a HttpException is raised.
        """

        try:
            sess = self._active_session_tokens[session_token]
        except KeyError:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session token.",
            ) from None

        self._active_session_tokens[session_token] = sess

        return sess

    async def _serve_index(
        self,
        request: fastapi.Request,
        initial_route_str: str,
    ) -> fastapi.responses.HTMLResponse:
        """
        Handler for serving the index HTML page via fastapi.
        """

        # Determine the initial route
        route_url = rx.URL(initial_route_str)
        initial_route = route_url.path.strip("/").split("/")

        # Create a session instance to hold all of this state in an organized
        # fashion.
        #
        # The session is still missing a lot of values at this point, such as
        # `send_message` and `receive_message`. It will be finished once the
        # websocket connection is established.
        session_token = secrets.token_urlsafe()
        sess = session.Session(
            app_server_=self,
            base_url=rx.URL(str(request.base_url)),
            initial_route=initial_route,
        )

        self._active_session_tokens[session_token] = sess

        # Add any attachments, except for user settings. These are deserialized
        # later on, once the client has sent the initial message.
        for attachment in self.default_attachments:
            if isinstance(attachment, user_settings_module.UserSettings):
                continue

            sess.attachments.add(copy.deepcopy(attachment))

        # Make sure a theme is attached
        if rx.Theme not in sess.attachments:
            thm = rx.Theme()
            sess.attachments.add(thm)
        else:
            thm = sess.attachments[rx.Theme]

        # Create a list of initial messages for the client to process
        initial_messages = [
            _build_set_theme_variables_message(thm),
        ]

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
                inspection.get_child_widget_containing_attribute_names_for_builtin_widgets()
            ),
        )

        html = html.replace(
            '"{initial_messages}"',
            json.dumps(initial_messages),
        )

        html = html.replace(
            '"{ping_pong_interval}"',
            str(self.app.ping_pong_interval.total_seconds()),
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
        if asset_id == "plotly.min.js" and plotly is not None:
            return fastapi.responses.Response(
                content=plotly.offline.get_plotlyjs(),
                media_type="text/javascript",
            )

        # Well known asset?
        if not asset_id.startswith("temp-"):
            # Construct the path to the target file
            asset_file_path = common.HOSTED_ASSETS_DIR / asset_id
            asset_file_path = asset_file_path.resolve()

            # Make sure the path is inside the hosted assets directory
            #
            # TODO: Is this safe? Would this allow the client to break out from
            # the directory using tricks such as "../", links, etc?
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
        sess = self.check_and_refresh_session(session_token)

        # Accept the socket
        await websocket.accept()

        # Create a function for sending messages to the frontend. This function
        # will also pipe the message to the validator if one is present.
        if self.validator_factory is None:
            sess._send_message = websocket.send_json  # type: ignore

            async def receive_message() -> uniserde.Jsonable:
                # Refresh the session's duration
                self._active_session_tokens[session_token] = sess

                # Fetch a message
                return await websocket.receive_json()

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

        # Upon connecting, the client sends an initial message containing
        # information about it. Wait for that.
        initial_message_json: Jsonable = await websocket.receive_json()
        initial_message = InitialClientMessage.from_json(initial_message_json)  # type: ignore

        sess.window_width = initial_message.window_width
        sess.window_height = initial_message.window_height

        # Parse the preferred locales
        preferred_locales = []

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

        # Publish the external URL via the session
        sess.external_url = (
            None
            if self.running_in_window
            else (
                initial_message.website_url
                if self.external_url_override is None
                else self.external_url_override
            )
        )

        # Deserialize the user settings
        visited_settings: Dict[str, user_settings_module.UserSettings] = {}

        for att_defaults in self.default_attachments:
            if not isinstance(att_defaults, user_settings_module.UserSettings):
                continue

            # Create the instance for this attachment. Bypass the constructor so
            # the instance doesn't immediately try to synchronize with the
            # frontend.
            att_instance = user_settings_module.UserSettings()
            object.__setattr__(
                att_instance,
                "__class__",
                type(att_defaults),
            )

            section_prefix = (
                f"{att_instance.section_name}:" if att_instance.section_name else ""
            )

            for py_field_name, field_type in inspection.get_type_annotations(
                type(att_instance)
            ).items():
                # Skip internal fields
                if py_field_name in user_settings_module.UserSettings.__annotations__:
                    continue

                # Make sure this field isn't clashing with another attachment
                doc_field_name = f"{section_prefix}{py_field_name}"

                try:
                    att_other = visited_settings[doc_field_name]
                except KeyError:
                    visited_settings[doc_field_name] = att_instance
                else:
                    raise RuntimeError(
                        f'The field "{py_field_name}" is used by multiple `UserSetting` attachments:\n'
                        f"- `{att_instance.__class__.__name__}` and \n"
                        f"- `{att_other.__class__.__name__}`.\n\n"
                        f"Rename one of the fields, or assign a `section_name` to one of the classes."
                    ) from None

                # Try to parse the field value
                try:
                    field_value = uniserde.from_json(
                        initial_message.user_settings[doc_field_name],
                        field_type,
                    )
                except (KeyError, uniserde.SerdeError):
                    field_value = copy.deepcopy(getattr(att_defaults, py_field_name))

                # Set the field value
                vars(att_instance)[py_field_name] = field_value

                # Attach the instance to the session
                sess.attachments._add(att_instance, synchronize=False)

        # Optionally create a validator
        validator_instance = (
            None if self.validator_factory is None else self.validator_factory(sess)
        )

        # Build the root widget
        global_state.currently_building_widget = None
        global_state.currently_building_session = sess

        try:
            sess._root_widget = self.app.build()
        finally:
            global_state.currently_building_session = None

        assert isinstance(
            sess._root_widget, rx.Widget
        ), f"The `build` function passed to the App must return a `Widget` instance, not {sess._root_widget!r}."

        # Trigger the `on_session_started` event
        await common.call_event_handler(self.on_session_start, sess)

        try:
            # Trigger a refresh. This will also send the initial state to the
            # frontend.
            #
            # This is done in a task, because the server is not yet running, so
            # the method would never receive a response, and thus would hang
            # indefinitely.
            asyncio.create_task(sess._refresh())

            # Serve the socket
            await sess.serve()

        # Don't spam the terminal just because a client disconnected
        except fastapi.WebSocketDisconnect:
            pass

        finally:
            # Fire the session end event
            await common.call_event_handler(self.on_session_end, sess)
