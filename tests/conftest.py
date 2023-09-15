import asyncio
import contextlib
from typing import AsyncGenerator, Container, List, Set

import babel
import pytest
from uniserde import Jsonable, JsonDoc

import reflex as rx
from reflex.app_server import AppServer


class _MockApp:
    def __init__(self, root_widget: rx.Widget):
        self._root_widget = root_widget

        self.outgoing_messages: List[JsonDoc] = []
        self._responses = asyncio.Queue()

        self._app = rx.App(lambda: root_widget)
        self._app_server = AppServer(
            self._app,
            external_url_override="https://unit.test",
            running_in_window=False,
            on_session_start=None,
            on_session_end=None,
            default_attachments=tuple(),
            validator_factory=None,
        )
        self._session = rx.Session(
            initial_route=[],
            send_message=self._send_message,  # type: ignore
            receive_message=self._receive_message,
            app_server_=self._app_server,
        )
        self._session._root_widget = root_widget
        self._session.external_url = None
        self.preferred_locales = (babel.Locale.parse("en_US"),)

        self._session._register_dirty_widget(
            root_widget,
            include_children_recursively=True,
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
                    for widget_id in message["params"]["deltaStates"]
                }

        return set()

    def get_build_output(self, widget: rx.Widget) -> rx.Widget:
        return self._session._weak_widget_data_by_widget[widget].build_result

    async def refresh(self) -> None:
        await self._session._refresh()


@contextlib.asynccontextmanager
async def _create_mockapp(root_widget: rx.Widget) -> AsyncGenerator[_MockApp, None]:
    app = _MockApp(root_widget)

    task = asyncio.create_task(app._session.serve())

    await app.refresh()

    try:
        yield app
    finally:
        task.cancel()


@pytest.fixture
def create_mockapp():
    return _create_mockapp
