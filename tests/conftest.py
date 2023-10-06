import asyncio
import collections
import contextlib
import types
from typing import *  # type: ignore

import babel
import pytest
from uniserde import Jsonable, JsonDoc

import rio
import rio.global_state
from rio.app_server import AppServer

T = TypeVar("T")
W = TypeVar("W", bound=rio.Component)


async def _make_awaitable(value: T = None) -> T:
    return value


def _fake_build_function() -> rio.Component:
    assert False, "This function should never be called"


async def _fake_send_message(message: Jsonable) -> None:
    pass


async def _fake_receive_message() -> Jsonable:
    while True:
        await asyncio.sleep(100000)


@pytest.fixture()
def enable_component_instantiation():
    app = rio.App(_fake_build_function)
    app_server = AppServer(
        app,
        running_in_window=False,
        on_session_start=None,
        on_session_end=None,
        default_attachments=tuple(),
        validator_factory=None,
    )
    session = rio.Session(
        app_server,
        rio.URL("https://unit.test"),
        rio.URL("https://unit.test"),
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
    def __init__(self, session: rio.Session) -> None:
        self._session = session
        self.outgoing_messages: List[JsonDoc] = []

        self._first_refresh_completed = asyncio.Event()

        self._responses = asyncio.Queue()
        self._responses.put_nowait(
            {
                "websiteUrl": "https://unit.test",
                "preferredLanguages": [],
                "userSettings": {},
                "windowWidth": 1920,
                "windowHeight": 1080,
            }
        )

    async def _send_message(self, message: JsonDoc) -> None:
        self.outgoing_messages.append(message)
        self._responses.put_nowait(
            {
                "jsonrpc": "2.0",
                "id": message["id"],
                "result": None,
            }
        )

        if message["method"] == "updateComponentStates":
            self._first_refresh_completed.set()

    async def _receive_message(self) -> Jsonable:
        return await self._responses.get()

    @property
    def dirty_components(self) -> Container[rio.Component]:
        return set(self._session._dirty_components)

    @property
    def last_updated_components(self) -> Set[rio.Component]:
        for message in reversed(self.outgoing_messages):
            if message["method"] == "updateComponentStates":
                return {
                    self._session._weak_components_by_id[component_id]
                    for component_id in message["params"]["deltaStates"]  # type: ignore
                    if component_id != self._session._root_component._id
                }

        return set()

    def get_root_component(self) -> rio.Component:
        sess = self._session
        return sess._weak_component_data_by_component[sess._root_component].build_result

    def get_component(self, component_type: Type[W]) -> W:
        for component in self._session._root_component._iter_component_tree():
            if type(component) is component_type:
                return component  # type: ignore

        raise AssertionError(f"No component of type {component_type} found")

    def get_build_output(self, component: rio.Component) -> rio.Component:
        return self._session._weak_component_data_by_component[component].build_result

    async def refresh(self) -> None:
        await self._session._refresh()


@contextlib.asynccontextmanager
async def _create_mockapp(
    build: Callable[[], rio.Component],
) -> AsyncGenerator[_MockApp, None]:
    app = rio.App(build)
    app_server = AppServer(
        app,
        running_in_window=False,
        on_session_start=None,
        on_session_end=None,
        default_attachments=tuple(),
        validator_factory=None,
    )

    # Emulate the process of creating a session as closely as possible
    fake_request: Any = types.SimpleNamespace(
        url="https://unit.test",
        base_url="https://unit.test",
        headers={"accept": "text/html"},
    )
    await app_server._serve_index(fake_request, "")

    [[session_token, session]] = app_server._active_session_tokens.items()
    mock_app = _MockApp(session)

    fake_websocket: Any = types.SimpleNamespace(
        accept=lambda: _make_awaitable(),
        send_json=mock_app._send_message,
        receive_json=mock_app._receive_message,
    )
    server_task = asyncio.create_task(
        app_server._serve_websocket(fake_websocket, session_token)
    )

    await mock_app._first_refresh_completed.wait()
    try:
        yield mock_app
    finally:
        server_task.cancel()


@pytest.fixture
def create_mockapp():
    yield _create_mockapp
