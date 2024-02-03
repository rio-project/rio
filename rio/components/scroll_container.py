from __future__ import annotations

from dataclasses import KW_ONLY
from typing import Literal

import rio

from .fundamental_component import FundamentalComponent

__all__ = ["ScrollContainer"]


class ScrollContainer(FundamentalComponent):
    """
    # ScrollContainer

    Displays a scroll bar if its child grows too large.

    `ScrollContainer` is a container which displays a scroll bar if its child
    component grows too large. It can scroll vertically and/or horizontally.

    ## Attributes:
    `content:` The child component to display inside the `ScrollContainer`.

    `scroll_x:` Controls horizontal scrolling. The default is `"auto"`, which
        means that a scroll bar will be displayed only if it is needed.
        `"always"` displays a scroll bar even if it isn't needed, and
        `"never"` disables horizontal scrolling altogether.

    `scroll_y:` Controls vertical scrolling. The default is `"auto"`, which
        means that a scroll bar will be displayed only if it is needed.
        `"always"` displays a scroll bar even if it isn't needed, and
        `"never"` disables vertical scrolling altogether.

    `sticky_bottom:` If `True`, when the user has scrolled to the bottom and
        the content of the `ScrollContainer` grows larger, the scroll bar
        will automatically scroll to the bottom again.

    ## Example:

    A simple `ScrollContainer` with a long text:
    TODO: check if it works :)
    ```python
    rio.ScrollContainer(
        content=rio.Text(
            content="This is a very long text that will be scrollable.",
        ),
    )
    ```
    """

    content: rio.Component
    _: KW_ONLY
    scroll_x: Literal["never", "auto", "always"] = "auto"
    scroll_y: Literal["never", "auto", "always"] = "auto"
    sticky_bottom: bool = False


ScrollContainer._unique_id = "ScrollContainer-builtin"
