from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from . import component_base

__all__ = [
    "ProgressBar",
]


class ProgressBar(component_base.FundamentalComponent):
    """
    A progress indicator in the shape of a horizontal bar.

    `ProgressBar` conveys to the user that activity is ongoing. It can either
    display the exact progress as a fraction from 0 to 1, or it can display an
    indeterminate progress animation, which is useful when the exact progress
    isn't known.

    The circular counterpart to this component is the `ProgressCircle`.

    Attributes:
        progress: The progress to display, as a fraction from 0 to 1. If `None`,
            the progress indicator will be indeterminate.
    """

    progress: Optional[float] = None


ProgressBar._unique_id = "ProgressBar-builtin"
