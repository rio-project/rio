from __future__ import annotations

from dataclasses import KW_ONLY, field
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "CustomListItem",
    "SingleLineListItem",
]


class CustomListItem(component_base.FundamentalComponent):
    child: component_base.Component
    _: KW_ONLY
    on_press: rio.EventHandler[[]] = None

    def _custom_serialize(self) -> JsonDoc:
        return {
            "pressable": self.on_press is not None,
        }


class SingleLineListItem(component_base.Component):
    text: str
    _: KW_ONLY
    image_or_icon: Optional[component_base.Component] = None
    actions: List[component_base.Component] = field(default_factory=list)
    on_press: rio.EventHandler[[]] = None

    def build(self) -> component_base.Component:
        children = []

        # Image or Icon
        if self.image_or_icon is not None:
            children.append(self.image_or_icon)

        # Main content (text)
        children.append(rio.Text(self.text))
        children.append(rio.Spacer())

        # Actions, if any
        children.extend(self.actions)

        # Combine everything
        return CustomListItem(
            child=rio.Row(
                *children,
                spacing=1,
                width="grow",
            ),
            on_press=self.on_press,
        )


CustomListItem._unique_id = "ListItem-builtin"
