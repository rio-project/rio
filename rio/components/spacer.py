from __future__ import annotations

from typing import *  # type: ignore

from . import class_container

__all__ = [
    "Spacer",
]


class Spacer(class_container.ClassContainer):
    def __init__(
        self,
        *,
        width: Union[Literal["grow"], float] = "grow",
        height: Union[Literal["grow"], float] = "grow",
        key: Optional[str] = None,
    ):
        super().__init__(
            None,
            ["rio-spacer"],
            key=key,
            width=width,
            height=height,
        )


# Make sure the widget is recognized as `ClassContainer`, rather than a new
# widget.
Spacer._unique_id = class_container.ClassContainer._unique_id
