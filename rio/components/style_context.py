from __future__ import annotations

from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "StyleContext",
]


class StyleContext(component_base.FundamentalComponent):
    child: Optional[rio.Component]
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
