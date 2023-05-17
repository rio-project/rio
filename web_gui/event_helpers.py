from __future__ import annotations

import inspect
import traceback
import typing
from typing import Any, Awaitable, Callable, Optional, TypeVar

from typing_extensions import ParamSpec

__all__ = [
    "EventHandler",
    "call_event_handler",
]


T = TypeVar("T")
P = ParamSpec("P")


EventHandler = Optional[Callable[P, Any | Awaitable[Any]]]


@typing.overload
async def call_event_handler(
    handler: EventHandler[[]],
) -> None:
    ...


@typing.overload
async def call_event_handler(
    handler: EventHandler[T],
    event_data: T,
) -> None:
    ...


async def call_event_handler(  # type: ignore
    handler: EventHandler[P],
    *event_data: T,  # type: ignore
) -> None:
    """
    Call an event handler, if one is present. Await it if necessary.
    """

    # Event handlers are optional
    if handler is None:
        return

    # If the handler is available, call it and await it if necessary
    try:
        result = handler(*event_data)  # type: ignore

        if inspect.isawaitable(result):
            await result

    # Display and discard exceptions
    except Exception:
        print("Exception in event handler:")
        traceback.print_exc()
