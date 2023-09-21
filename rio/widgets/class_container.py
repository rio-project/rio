from __future__ import annotations

from typing import *  # type: ignore

import rio

from . import widget_base

__all__ = [
    "ClassContainer",
]


class ClassContainer(widget_base.FundamentalWidget):
    """
    Widget which holds a single child, and applies a list of CSS classes to it.
    This is enough to implement several widgets, preventing the need to create a
    whole bunch of almost identical JavaScript widgets.

    This widget is only intended for internal use and is not part of the public
    API.
    """

    child: Optional[rio.Widget]
    classes: List[str]


ClassContainer._unique_id = "ClassContainer-builtin"
