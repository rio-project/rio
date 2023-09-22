from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from typing import *  # type: ignore

from typing_extensions import TypeAlias

import rio

__all__ = [
    "Route",
]


@dataclass(frozen=True)
class Route:
    name: str
    build: Callable[[], rio.Widget]
    _: KW_ONLY
    children: List["Route"] = field(default_factory=list)
    guard: Optional[Callable[[rio.Session], Optional[str]]] = None
