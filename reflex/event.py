from __future__ import annotations

import enum
from typing import *  # type: ignore

import reflex as rx

__all__ = [
    "on_route_change",
]


T = TypeVar("T", bound="rx.Widget")


class EventTag(enum.Enum):
    ON_ROUTE_CHANGE = enum.auto()


def on_route_change(func: Callable[[T], None]) -> Callable[[T], None]:
    func._reflex_session_event_tag_ = EventTag.ON_ROUTE_CHANGE
    return func
