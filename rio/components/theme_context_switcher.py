from __future__ import annotations

from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .fundamental_component import FundamentalComponent

__all__ = [
    "ThemeContextSwitcher",
]


class ThemeContextSwitcher(FundamentalComponent):
    content: rio.Component
    color: rio.ColorSet

    def _custom_serialize(self) -> JsonDoc:
        return {
            "color": self.session.theme._serialize_colorset(self.color),
        }


ThemeContextSwitcher._unique_id = "ThemeContextSwitcher-builtin"
