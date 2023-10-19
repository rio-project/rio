from dataclasses import KW_ONLY
from typing import *  # type: ignore

from .component_base import Component, FundamentalComponent

__all__ = ["ScrollContainer"]


class ScrollContainer(FundamentalComponent):
    """
    Displays a scroll bar if its child grows too large.

    `ScrollContainer` is a container which displays a scroll bar if its child
    component grows too large. It can scroll vertically and/or horizontally.

    Attributes:
        child: The child component to display inside the `ScrollContainer`.

        scroll_x: Controls horizontal scrolling. The default is `"auto"`, which
            means that a scroll bar will be displayed only if it is needed.
            `"always"` displays a scroll bar even if it isn't needed, and
            `"never"` disables horizontal scrolling altogether.

        scroll_y: Controls vertical scrolling. The default is `"auto"`, which
            means that a scroll bar will be displayed only if it is needed.
            `"always"` displays a scroll bar even if it isn't needed, and
            `"never"` disables vertical scrolling altogether.
    """

    child: Component
    _: KW_ONLY
    scroll_x: Literal["never", "auto", "always"] = "auto"
    scroll_y: Literal["never", "auto", "always"] = "auto"


ScrollContainer._unique_id = "ScrollContainer-builtin"
