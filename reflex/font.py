from pathlib import Path
from typing import *  # type: ignore


__all__ = [
    "Font",
]


class Font:
    def __init__(
        self,
        name: str,
    ) -> None:
        self.name = name
