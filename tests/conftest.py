import asyncio
import contextlib
import types
from typing import *  # type: ignore

import babel
import pytest
from uniserde import Jsonable, JsonDoc

import rio
import rio.global_state
from rio.app_server import AppServer


def _fake_build_function() -> rio.Widget:
    assert False, "This function should never be called"


async def _fake_send_message(message: Jsonable) -> None:
    pass


async def _fake_receive_message() -> Jsonable:
    while True:
        await asyncio.sleep(100000)


@pytest.fixture()
def enable_widget_instantiation():
    app = rio.App(_fake_build_function)
    app_server = AppServer(
        app,
        external_url_override="https://unit.test",
        running_in_window=False,
        on_session_start=None,
        on_session_end=None,
        default_attachments=tuple(),
        validator_factory=None,
    )
    session = rio.Session(
        app_server,
        rio.URL("https://unit.test"),
        (),
    )
    session.external_url = None
    session.preferred_locales = (babel.Locale.parse("en_US"),)
    session._send_message = _fake_send_message
    session._receive_message = _fake_receive_message

    rio.global_state.currently_building_session = session

    try:
        yield session
    finally:
        rio.global_state.currently_building_session = None


class _MockApp:
    _session: rio.Session

    def __init__(self):
        self.outgoing_messages: List[JsonDoc] = []
        self._responses = asyncio.Queue()

    async def _send_message(self, message: JsonDoc) -> None:
        self.outgoing_messages.append(message)
        self._responses.put_nowait(
            {
                "jsonrpc": "2.0",
                "id": message["id"],
                "result": None,
            }
        )

    async def _receive_message(self) -> Jsonable:
        return await self._responses.get()

    @property
    def dirty_widgets(self) -> Container[rio.Widget]:
        return set(self._session._dirty_widgets)

    @property
    def last_updated_widgets(self) -> Set[rio.Widget]:
        for message in reversed(self.outgoing_messages):
            if message["method"] == "updateWidgetStates":
                return {
                    self._session._weak_widgets_by_id[widget_id]
                    for widget_id in message["params"]["deltaStates"]  # type: ignore
                }

        return set()

    def get_build_output(self, widget: rio.Widget) -> rio.Widget:
        return self._session._weak_widget_data_by_widget[widget].build_result

    async def refresh(self) -> None:
        await self._session._refresh()

        rio.global_state.currently_building_session = self._session


@contextlib.asynccontextmanager
async def _create_mockapp(
    root_widget: rio.Widget,
) -> AsyncGenerator[_MockApp, None]:
    # Tests often operate on widget instances - mutating them, refreshing them,
    # etc. But widget's can only be instantiated in `build` functions, so we
    # must pretend that a build function is running. To do this, we need to
    # create a Session and set it as the "currently active session".
    app = rio.App(lambda: root_widget)
    app_server = AppServer(
        app,
        external_url_override="https://unit.test",
        running_in_window=False,
        on_session_start=None,
        on_session_end=None,
        default_attachments=tuple(),
        validator_factory=None,
    )

    # Emulate the process of creating a session as closely as possible
    fake_request: Any = types.SimpleNamespace(base_url="https://unit.test")
    await app_server._serve_index(fake_request, "")

    [[session_token, session]] = app_server._active_session_tokens.items()
    mock_app = _MockApp()
    session._send_message = mock_app._send_message  # type: ignore
    session._receive_message = mock_app._receive_message

    fake_websocket: Any = types.SimpleNamespace()
    await app_server._serve_websocket(fake_websocket, session_token)

    yield mock_app


@pytest.fixture
def create_mockapp():
    yield _create_mockapp
