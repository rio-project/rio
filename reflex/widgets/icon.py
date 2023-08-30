from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore
from . import widget_base

from uniserde import JsonDoc

import reflex as rx

__all__ = [
    "Icon",
]

_ICONS: Dict[str, Dict[str, List[Tuple[float, float]]]] = {}


class Icon(widget_base.HtmlWidget):
    icon: str
    _: KW_ONLY
    fill_mode: Literal["fit", "stretch", "tile", "zoom"] = "fit"
    fill: Optional[rx.FillLike] = None

    @property
    def _icon_set_and_name(self) -> Tuple[str, str]:
        pos = self.icon.find("/")

        if pos == -1:
            raise ValueError(
                f"Icon names should be of the form `set/name`, not `{self.icon}`"
            )

        return self.icon[:pos], self.icon[pos + 1 :]

    def _custom_serialize(self) -> JsonDoc:
        # Find the icon path
        set_name, icon_name = self._icon_set_and_name

        try:
            icon_set = _ICONS[set_name]
        except KeyError:
            raise ValueError(f"There is no icon set named `{set_name}`")

        try:
            icon_path = icon_set[icon_name]
        except KeyError:
            raise ValueError(
                f"There is no icon named `{icon_name}` in set `{set_name}`"
            )

        # Determine the fill
        if self.fill is None:
            thm = self.session.attachments[rx.Theme]
            fill = thm.text_style.font_color
        else:
            fill = self.fill

        # Serialize
        return {
            "iconPath": icon_path,  # type: ignore
            "fill": rx.Fill._try_from(fill)._serialize(),
        }


Icon._unique_id = "Icon-builtin"
