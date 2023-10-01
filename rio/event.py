from __future__ import annotations

import enum
from typing import *  # type: ignore

import rio

T = TypeVar("T", bound="rio.Widget")
U = TypeVar("U")


class EventTag(enum.Enum):
    ON_CREATE = enum.auto()
    ON_ROUTE_CHANGE = enum.auto()


def on_create(handler: Callable[[T], None]) -> Callable[[T], None]:
    handler._rio_event_tag_ = EventTag.ON_CREATE
    return handler


def on_route_change(handler: Callable[[T], U]) -> Callable[[T], U]:
    handler._rio_event_tag_ = EventTag.ON_ROUTE_CHANGE
    return handler
