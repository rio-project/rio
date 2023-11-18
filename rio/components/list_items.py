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

    async def _on_message(self, msg: Any) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg
        assert msg["type"] == "press", msg

        msg_type: str = msg["type"]
        assert isinstance(msg_type, str), msg_type

        if self.on_press is None:
            return

        # Trigger the press event
        await self.call_event_handler(self.on_press)

        # Refresh the session
        await self.session._refresh()


class SingleLineListItem(component_base.Component):
    text: str
    _: KW_ONLY
    secondary_text: str = ""
    image_or_icon: Optional[component_base.Component] = None
    actions: List[component_base.Component] = field(default_factory=list)
    on_press: rio.EventHandler[[]] = None

    def build(self) -> component_base.Component:
        children = []

        # Image or Icon
        if self.image_or_icon is not None:
            children.append(self.image_or_icon)

        # Main content (text)
        text_children = [
            rio.Text(
                self.text,
                align_x=0,
            )
        ]

        if self.secondary_text:
            text_children.append(
                rio.Text(
                    self.secondary_text,
                    multiline=True,
                    style="dim",
                    align_x=0,
                )
            )

        if len(text_children) == 1:
            children.append(text_children[0])
        else:
            children.append(
                rio.Column(
                    *text_children,
                    spacing=0.5,
                )
            )

        # Space

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
