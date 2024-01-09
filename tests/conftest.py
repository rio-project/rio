import asyncio
from typing import *  # type: ignore

import pytest
from uniserde import Jsonable

import rio
import rio.global_state
from rio.app_server import AppServer

T = TypeVar("T")
W = TypeVar("W", bound=rio.Component)


def _fake_build_function() -> rio.Component:
    assert False, "This function should never be called"


async def _fake_send_message(message: Jsonable) -> None:
    pass


async def _fake_receive_message() -> Jsonable:
    while True:
        await asyncio.sleep(100000)


@pytest.fixture()
def enable_component_instantiation():
    app = rio.App(build=_fake_build_function)
    app_server = AppServer(
        app_=app,
        debug_mode=False,
        running_in_window=False,
        validator_factory=None,
        internal_on_app_start=None,
    )
    session = rio.Session(
        app_server,
        "<a fake session token>",
        rio.URL("https://unit.test"),
        rio.URL("https://unit.test"),
    )
    session.external_url = None
    session._decimal_separator = "."
    session._thousands_separator = ","
    session._send_message = _fake_send_message
    session._receive_message = _fake_receive_message

    rio.global_state.currently_building_session = session

    try:
        yield session
    finally:
        rio.global_state.currently_building_session = None
