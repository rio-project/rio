from __future__ import annotations

import rio

from .fundamental_component import FundamentalComponent

__all__ = [
    "Switcher",
]


class Switcher(FundamentalComponent):
    child: rio.Component | None


Switcher._unique_id = "Switcher-builtin"
