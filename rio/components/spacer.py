from __future__ import annotations

from typing import *  # type: ignore

from . import class_container

__all__ = [
    "Spacer",
]


class Spacer(class_container.ClassContainer):
    """
    Adds empty space.

    Spacers are invisible components which add empty space between other
    components. While similar effects can often be achieved using margins and
    alignment, code with spacers can sometimes be easier to read.

    Note that unlike most components in Rio, `Spacer` does not have a `natural`
    size. Therefore it defaults to a width and height of `grow`, as that is how
    they're frequently used.
    """

    def __init__(
        self,
        *,
        width: Union[Literal["grow"], float] = "grow",
        height: Union[Literal["grow"], float] = "grow",
        key: Optional[str] = None,
    ):
        """
        Args:
            width: How much space the spacer should take up horizontally.
            height: How much space the spacer should take up vertically.
        """

        super().__init__(
            None,
            ["rio-spacer"],
            key=key,
            width=width,
            height=height,
        )


# Make sure the component is recognized as `ClassContainer`, rather than a new
# component.
Spacer._unique_id = class_container.ClassContainer._unique_id
