import asyncio
import copy
from typing import Container, List, Mapping

import pytest
from uniserde import Jsonable

import reflex as rx
from reflex.app_server import AppServer


class _MockApp:
    def __init__(self, root_widget: rx.Widget):
        self._root_widget = root_widget

        self.outgoing_messages: List[Jsonable] = []

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
            root_widget=root_widget,
            initial_route=[],
            send_message=self._send_message,
            receive_message=self._receive_message,
            app_server_=self._app_server,
        )

        self._session._register_dirty_widget(
            root_widget, include_fundamental_children_recursively=True
        )

    async def _send_message(self, message: Jsonable) -> None:
        self.outgoing_messages.append(message)

    async def _receive_message(self) -> Jsonable:
        raise NotImplementedError("This is a placeholder that should never be called")

    @property
    def dirty_widgets(self) -> Container[rx.Widget]:
        return set(self._session._dirty_widgets)

    def get_build_output(self, widget: rx.Widget) -> rx.Widget:
        return self._session._weak_widget_data_by_widget[widget].build_result

    async def refresh(self) -> None:
        await self._session._refresh()


async def _create_mockapp(root_widget: rx.Widget) -> _MockApp:
    app = _MockApp(root_widget)
    await app.refresh()
    return app


@pytest.fixture
def MockApp():
    return _create_mockapp
