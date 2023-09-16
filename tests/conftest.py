import asyncio
import contextlib
from typing import AsyncGenerator, Container, List, Set

import babel
import pytest
from uniserde import Jsonable, JsonDoc

import reflex as rx
import reflex.global_state
from reflex.app_server import AppServer


def _fake_build_function() -> rx.Widget:
    assert False, "This function should never be called"


async def _fake_send_message(message: Jsonable) -> None:
    pass


async def _fake_receive_message() -> Jsonable:
    while True:
        await asyncio.sleep(100000)


@contextlib.contextmanager
def _enable_widget_instantiation(
    send_message=_fake_send_message,
    receive_message=_fake_receive_message,
):
    app = rx.App(_fake_build_function)
    app_server = AppServer(
        app,
        external_url_override="https://unit.test",
        running_in_window=False,
        on_session_start=None,
        on_session_end=None,
        default_attachments=tuple(),
        validator_factory=None,
    )
    session = rx.Session(
        initial_route=[],
        send_message=send_message,
        receive_message=receive_message,
        app_server_=app_server,
    )
    session.external_url = None
    session.preferred_locales = (babel.Locale.parse("en_US"),)

    reflex.global_state.currently_building_session = session

    try:
        yield session
    finally:
        reflex.global_state.currently_building_session = None


@pytest.fixture()
def enable_widget_instantiation():
    with _enable_widget_instantiation():
        yield


class _MockApp:
    _session: rx.Session

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
    def dirty_widgets(self) -> Container[rx.Widget]:
        return set(self._session._dirty_widgets)

    @property
    def last_updated_widgets(self) -> Set[rx.Widget]:
        for message in reversed(self.outgoing_messages):
            if message["method"] == "updateWidgetStates":
                return {
                    self._session._weak_widgets_by_id[widget_id]
                    for widget_id in message["params"]["deltaStates"]  # type: ignore
                }

        return set()

    def get_build_output(self, widget: rx.Widget) -> rx.Widget:
        return self._session._weak_widget_data_by_widget[widget].build_result

    async def refresh(self) -> None:
        await self._session._refresh()

        reflex.global_state.currently_building_session = self._session


@pytest.fixture
def create_mockapp():
    # Tests often operate on widget instances - mutating them, refreshing them,
    # etc. But widget's can only be instantiated in `build` functions, so we
    # must pretend that a build function is running. To do this, we need to
    # create a Session and set it as the "currently active session".
    @contextlib.asynccontextmanager
    async def _create_mockapp(root_widget: rx.Widget) -> AsyncGenerator[_MockApp, None]:
        session._root_widget = root_widget

        # Start a task that processes outgoing websocket/unicall messages
        task = asyncio.create_task(session.serve())
        await mock_app.refresh()

        try:
            yield mock_app
        finally:
            task.cancel()

    mock_app = _MockApp()

    with _enable_widget_instantiation(
        mock_app._send_message, mock_app._receive_message
    ) as session:
        mock_app._session = session

        yield _create_mockapp
