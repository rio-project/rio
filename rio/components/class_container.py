from __future__ import annotations

from typing import *  # type: ignore

import rio

from . import component_base

__all__ = [
    "ClassContainer",
]


class ClassContainer(component_base.FundamentalComponent):
    """
    Component which holds a single child, and applies a list of CSS classes to it.
    This is enough to implement several components, preventing the need to create a
    whole bunch of almost identical JavaScript components.

    This component is only intended for internal use and is not part of the public
    API.
    """

    child: Optional[rio.Component]
    classes: List[str]


ClassContainer._unique_id = "ClassContainer-builtin"
