from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore
from . import widget_base

from uniserde import JsonDoc

import reflex as rx

__all__ = [
    "Icon",
]


# Icon set -> Icon
# Each Icon is a tuple
# - width
# - height
# - path. This is stored as the value which must be assigned to the SVG's `d`
#   attribute.
_ICONS: Dict[str, Dict[str, Tuple[float, float, str]]] = {}


class Icon(widget_base.HtmlWidget):
    icon: str
    _: KW_ONLY
    fill_mode: Literal["fit", "stretch", "tile", "zoom"] = "fit"
    fill: Optional[rx.FillLike] = None

    @staticmethod
    def add_icon_set(
        set_name: str,
        icon_set: Dict[str, Tuple[float, float, str]],
    ) -> None:
        """
        Add an icon set to the global registry. This allows the icons to be
        accessed as `set_name/icon_name`.

        There must not already be a set with the given name.

        The icon set is a dictionary mapping icon names to tuples of the form

        - width
        - height
        - path

        The path is the value which must be assigned to the SVG's `d` attribute
        to draw the icon.
        """
        if set_name in _ICONS:
            raise ValueError(f"There is already a set named `{set_name}`")

        _ICONS[set_name] = icon_set

    @property
    def _icon_set_and_name(self) -> Tuple[str, str]:
        pos = self.icon.find("/")

        if pos == -1:
            return "reflex", self.icon

        return self.icon[:pos], self.icon[pos + 1 :]

    def _custom_serialize(self) -> JsonDoc:
        # Find the icon path
        set_name, icon_name = self._icon_set_and_name

        try:
            icon_set = _ICONS[set_name]
        except KeyError:
            raise ValueError(f"There is no icon set named `{set_name}`")

        try:
            width, height, icon_path = icon_set[icon_name]
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
            "width": width,
            "height": height,
            "path": icon_path,
            "fill": rx.Fill._try_from(fill)._serialize(),
        }


Icon._unique_id = "Icon-builtin"
