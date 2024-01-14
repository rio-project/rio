from __future__ import annotations

from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .. import color
from . import component_base

__all__ = [
    "ThemeContextSwitcher",
]


class ThemeContextSwitcher(component_base.FundamentalComponent):
    child: rio.Component
    color: color.ColorSet

    def _custom_serialize(self) -> JsonDoc:
        return {
            "color": self.session.theme._serialize_colorset(self.color),
        }


ThemeContextSwitcher._unique_id = "ThemeContextSwitcher-builtin"
