from __future__ import annotations

from typing import Literal

from uniserde import JsonDoc

import rio

from .fundamental_component import FundamentalComponent

__all__ = [
    "StyleContext",
]


class StyleContext(FundamentalComponent):
    child: rio.Component | None
    context: Literal[
        "background",
        "neutral",
        "primary",
        "secondary",
        "success",
        "warning",
        "danger",
    ]

    def _custom_serialize(self) -> JsonDoc:
        return {
            "classes": [
                f"rio-switcheroo-{self.context}",
            ],
        }


# Pretend this is a class container, since applying a switcheroo is all that's
# necessary
StyleContext._unique_id = "ClassContainer-builtin"
