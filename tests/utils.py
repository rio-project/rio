import asyncio
import contextlib
import types
from typing import *

from uniserde import Jsonable, JsonDoc

import rio
from rio.app_server import AppServer

T = TypeVar("T")
C = TypeVar("C", bound=rio.Component)


async def _make_awaitable(value: T = None) -> T:
    return value


class MockApp:
    def __init__(
        self,
        session: rio.Session,
        user_settings: JsonDoc = {},
    ) -> None:
        self._session = session
        self.outgoing_messages: List[JsonDoc] = []

        self._first_refresh_completed = asyncio.Event()

        self._responses = asyncio.Queue[JsonDoc]()
        self._responses.put_nowait(
            {
                "websiteUrl": "https://unit.test",
                "preferredLanguages": [],
                "userSettings": user_settings,
                "windowWidth": 1920,
                "windowHeight": 1080,
                "timezone": "America/New_York",
                "prefersLightTheme": True,
            }
        )

    async def _send_message(self, message: JsonDoc) -> None:
        self.outgoing_messages.append(message)

        if "id" in message:
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

    def get_component(self, component_type: Type[C]) -> C:
        for component in self._session._root_component._iter_component_tree():
            if type(component) is component_type:
                return component  # type: ignore

        raise AssertionError(f"No component of type {component_type} found")

    def get_build_output(
        self,
        component: rio.Component,
        type_: Optional[Type[C]] = None,
    ) -> C:
        result = self._session._weak_component_data_by_component[component].build_result

        if type_ is not None:
            assert type(result) is type_, f"Expected {type_}, got {type(result)}"

        return result  # type: ignore

    async def refresh(self) -> None:
        await self._session._refresh()


@contextlib.asynccontextmanager
async def create_mockapp(
    build: Callable[[], rio.Component] = lambda: rio.Text("hi"),
    *,
    app_name: str = "mock-app",
    running_in_window: bool = False,
    user_settings: JsonDoc = {},
    default_attachments: Iterable[object] = (),
) -> AsyncGenerator[MockApp, None]:
    app = rio.App(build=build, name=app_name)
    app_server = AppServer(
        app,
        running_in_window=running_in_window,
        on_session_start=None,
        on_session_end=None,
        default_attachments=tuple(default_attachments),
        validator_factory=None,
        internal_on_app_start=None,
    )

    # Emulate the process of creating a session as closely as possible
    fake_request: Any = types.SimpleNamespace(
        url="https://unit.test",
        base_url="https://unit.test",
        headers={"accept": "text/html"},
    )
    await app_server._serve_index(fake_request, "")

    [[session_token, session]] = app_server._active_session_tokens.items()
    mock_app = MockApp(session, user_settings=user_settings)

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
