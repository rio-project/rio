from __future__ import annotations

from dataclasses import KW_ONLY
from pathlib import Path
from typing import *  # type: ignore

from uniserde import JsonDoc

import reflex as rx

from .. import color, fills, icon_registry
from . import widget_base

__all__ = [
    "Icon",
]


class Icon(widget_base.FundamentalWidget):
    icon: str
    _: KW_ONLY
    fill: Union[rx.FillLike, color.ColorSet] = "default"

    @staticmethod
    def _get_registry() -> icon_registry.IconRegistry:
        return icon_registry.IconRegistry.get_singleton()

    @staticmethod
    def register_icon_set(
        set_name: str,
        icon_set_zip_path: Path,
    ) -> None:
        """
        Add an icon set to the global registry. This allows the icons to be
        accessed as `set_name/icon_name` or `set_name/icon_name/variant`.

        There must not already be a set with the given name.

        The icon set is a zip containing SVG files. The SVG files must have a
        `viewBox` attribute, but no height or width. They will be colored by the
        `fill` property of the `Icon` widget.

        Files located in the root of the archive can be accessed as
        `set_name/icon_name`. Files located in a subdirectory can be accessed as
        `set_name/icon_name/variant`.
        """
        registry = Icon._get_registry()

        if set_name in registry.icon_set_archives:
            raise ValueError(f"There is already an icon set named `{set_name}`")

        registry.icon_set_archives[set_name] = icon_set_zip_path

    def _custom_serialize(self) -> JsonDoc:
        # Get the icon's SVG
        registry = Icon._get_registry()
        svg_source = registry.get_icon_svg(self.icon)

        # Serialize the fill. This isn't automatically handled because it's a
        # Union.
        if isinstance(self.fill, fills.Fill):
            fill = self.fill._serialize(self.session)
        elif isinstance(self.fill, color.Color):
            fill = self.fill.rgba
        else:
            assert isinstance(self.fill, str), f"Unsupported fill type: {self.fill}"
            fill = self.fill

        # Serialize the width and height, as specified in Python. These will be
        # used to force the actual graphic to be the correct height, while the
        # rest is empty space.
        width = self.width if isinstance(self.width, float) else None

        # Serialize
        return {
            "svgSource": svg_source,
            "fill": fill,
        }


Icon._unique_id = "Icon-builtin"
