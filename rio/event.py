from __future__ import annotations

import enum
from typing import *  # type: ignore

import rio

C = TypeVar("C", bound="rio.Component")
R = TypeVar("R")


class EventTag(enum.Enum):
    ON_CREATE = enum.auto()
    ON_PAGE_CHANGE = enum.auto()


def on_create(handler: Callable[[C], None]) -> Callable[[C], None]:
    handler._rio_event_tag_ = EventTag.ON_CREATE
    return handler


def on_page_change(handler: Callable[[C], R]) -> Callable[[C], R]:
    handler._rio_event_tag_ = EventTag.ON_PAGE_CHANGE
    return handler
