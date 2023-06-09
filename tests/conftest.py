import pytest

import asyncio
from typing import Container, List, Mapping

import reflex as rx
from reflex.app_server import AppServer
from reflex.messages import OutgoingMessage


class _MockApp:
    def __init__(self, root_widget: rx.Widget):
        self._root_widget = root_widget

        self.outgoing_messages: List[OutgoingMessage] = []

        self._app = rx.App("MockApp", lambda: root_widget)
        self._app_server = AppServer(
            self._app,
            external_url="https://unit.test",
            on_session_started=None,
            validator_factory=None,
        )
        self._session = rx.Session(
            root_widget,
            self._send_message,
            self._app_server,
        )

        self._session.register_dirty_widget(
            root_widget, include_fundamental_children_recursively=True
        )
        asyncio.run(self._session.refresh())

    async def _send_message(self, message: OutgoingMessage) -> None:
        self.outgoing_messages.append(message)

    @property
    def dirty_widgets(self) -> Container[rx.Widget]:
        return set(self._session._dirty_widgets)

    def get_build_output(self, widget: rx.Widget) -> rx.Widget:
        return self._session._weak_widget_data_by_widget[widget].build_result


@pytest.fixture
def MockApp():
    return _MockApp
