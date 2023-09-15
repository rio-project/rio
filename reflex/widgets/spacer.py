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
        key: Optional[str] = None,
    ):
        super().__init__(
            None,
            ["reflex-spacer"],
            key=key,
            width="grow",
            height="grow",
        )


# Make sure the widget is recognized as `ClassContainer`, rather than a new
# widget.
Spacer._unique_id = class_container.ClassContainer._unique_id
