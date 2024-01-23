from __future__ import annotations

import collections
import enum
from datetime import timedelta
from typing import *  # type: ignore

import rio

__all__ = [
    "on_page_change",
    "on_mount",
    "on_unmount",
    "periodic",
]

C = TypeVar("C", bound="rio.Component")
R = TypeVar("R")
SyncOrAsync = R | Awaitable[R]
SyncOrAsyncNone = TypeVar("SyncOrAsyncNone", bound=SyncOrAsync[None])


class EventTag(enum.Enum):
    ON_POPULATE = enum.auto()
    ON_PAGE_CHANGE = enum.auto()
    ON_MOUNT = enum.auto()
    ON_UNMOUNT = enum.auto()
    PERIODIC = enum.auto()


def _register_as_event_handler(function: Callable, tag: EventTag, args: Any) -> None:
    all_events: dict[EventTag, list[Any]] = vars(function).setdefault(
        "_rio_events_", {}
    )
    events_like_this = all_events.setdefault(tag, [])
    events_like_this.append(args)


def on_populate(handler: Callable[[C], R]) -> Callable[[C], R]:
    """
    Triggered after the component has been created or has been reconciled. This
    allows you to asynchronously fetch any data which depends on the component's
    state.
    """
    _register_as_event_handler(handler, EventTag.ON_POPULATE, None)
    return handler


def on_page_change(handler: Callable[[C], R]) -> Callable[[C], R]:
    """
    Triggered whenever the session changes pages.
    """
    _register_as_event_handler(handler, EventTag.ON_PAGE_CHANGE, None)
    return handler


def on_mount(handler: Callable[[C], R]) -> Callable[[C], R]:
    """
    Triggered when the component is added to the component tree.

    This may be triggered multiple times if the component is removed and then
    re-added.
    """
    _register_as_event_handler(handler, EventTag.ON_MOUNT, None)
    return handler


def on_unmount(handler: Callable[[C], R]) -> Callable[[C], R]:
    """
    Triggered when the component is removed from the component tree.

    This may be triggered multiple times if the component is removed and then
    re-added.
    """
    _register_as_event_handler(handler, EventTag.ON_UNMOUNT, None)
    return handler


def periodic(
    interval: float | timedelta,
) -> Callable[[Callable[[C], SyncOrAsyncNone]], Callable[[C], SyncOrAsyncNone]]:
    """
    TODO / unfinished / do not use

    This event is triggered repeatedly at a fixed time interval for as long as
    the component exists. The component does not have to be mounted for this
    event to trigger.

    The interval only starts counting after the previous handler has finished
    executing, so the handler will never run twice simultaneously, even if it
    takes longer than the interval to execute.

    Args:
        period: The number of seconds, or timedelta, between each trigger.
    """
    # Convert timedelta to float
    if isinstance(interval, timedelta):
        interval = interval.total_seconds()

    def decorator(
        handler: Callable[[C], SyncOrAsyncNone]
    ) -> Callable[[C], SyncOrAsyncNone]:
        _register_as_event_handler(handler, EventTag.PERIODIC, interval)
        return handler

    return decorator
