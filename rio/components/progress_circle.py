from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from . import component_base

__all__ = [
    "ProgressCircle",
]


class ProgressCircle(component_base.FundamentalComponent):
    """
    A progress indicator in the shape of a circle.

    `ProgressCircle` conveys to the user that activity is ongoing. It can either
    display the exact progress as a fraction from 0 to 1, or it can display an
    indeterminate progress animation, which is useful when the exact progress
    isn't known.

    The linear counterpart to this component is the `ProgressBar`.

    Attributes:
        progress: The progress to display, as a fraction from 0 to 1. If `None`,
            the progress indicator will be indeterminate.

        color: The color scheme of the progress indicator. Keeping the default
                is recommended, but it may make sense to change the color in
                case the default is hard to perceive on your background.
    """

    progress: Optional[float]
    color: rio.ColorSet

    def __init__(
        self,
        *,
        progress: Optional[float] = None,
        color: rio.ColorSet = "keep",
        size: Union[Literal["grow"], float] = 3.5,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        """
        Args:
            progress: The progress to display, as a fraction from 0 to 1. If `None`,
                the progress indicator will be indeterminate.

            color: The color scheme of the progress indicator. Keeping the default
                is recommended, but it may make sense to change the color in case
                the default is hard to perceive on your background.

            size: The size of the progress indicator. This is equivalent to setting
                a component's `width` and `height` to the same value.

                Note that unlike most components in Rio, `ProgressCircle` does not
                have a `natural` size, since the circle can easily be scaled to fit
                any size. Therefore it defaults to a reasonable size which should
                fit most use cases.
        """
        super().__init__(
            key=key,
            margin=margin,
            margin_x=margin_x,
            margin_y=margin_y,
            margin_left=margin_left,
            margin_top=margin_top,
            margin_right=margin_right,
            margin_bottom=margin_bottom,
            width=size,
            height=size,
            align_x=align_x,
            align_y=align_y,
        )

        self.progress = progress
        self.color = color


ProgressCircle._unique_id = "ProgressCircle-builtin"
