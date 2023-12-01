from __future__ import annotations

import enum
from datetime import timedelta
from typing import *  # type: ignore

import rio

__all__ = [
    "on_create",
    "on_page_change",
    "on_mount",
    "on_unmount",
    "periodic",
]

C = TypeVar("C", bound="rio.Component")
R = TypeVar("R")
SyncOrAsync = Union[R, Awaitable[R]]
SyncOrAsyncNone = TypeVar("SyncOrAsyncNone", bound=SyncOrAsync[None])


class EventTag(enum.Enum):
    ON_CREATE = enum.auto()
    ON_PAGE_CHANGE = enum.auto()
    ON_MOUNT = enum.auto()
    ON_UNMOUNT = enum.auto()
    PERIODIC = enum.auto()


def _register_as_event_handler(function: Callable, tag: EventTag, args: Any) -> None:
    tags_dict = vars(function).setdefault("_rio_event_tags_", {})
    tags_dict[tag] = args


def on_create(handler: Callable[[C], None]) -> Callable[[C], None]:
    """
    Triggered after the component has been created and has access to all of its
    attributes and session. Use this if you need to do any setup that requires
    accessing the component's attributes.

    Accessing attributes in `__init__` doesn't work reliably, because the state
    bindings are only initialized after `__init__` has run.
    """
    handler._rio_event_tag_ = EventTag.ON_CREATE
    return handler


def on_page_change(handler: Callable[[C], R]) -> Callable[[C], R]:
    """
    Triggered whenever the session changes pages.
    """
    handler._rio_event_tag_ = EventTag.ON_PAGE_CHANGE
    return handler


def on_mount(handler: Callable[[C], R]) -> Callable[[C], R]:
    """
    Triggered when the component is added to the widget tree.

    This may be triggered multiple times if the component is removed and then
    re-added.
    """
    handler._rio_event_tag_ = EventTag.ON_MOUNT
    return handler


def on_unmount(handler: Callable[[C], R]) -> Callable[[C], R]:
    """
    Triggered when the component is removed from the widget tree.

    This may be triggered multiple times if the component is removed and then
    re-added.
    """
    handler._rio_event_tag_ = EventTag.ON_UNMOUNT
    return handler


def periodic(
    interval: Union[float, timedelta]
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
        handler._rio_event_tag_ = EventTag.PERIODIC
        handler._rio_event_periodic_interval_ = interval
        return handler

    return decorator
