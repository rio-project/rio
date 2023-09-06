from __future__ import annotations

from dataclasses import KW_ONLY
from pathlib import Path
from typing import *  # type: ignore

from uniserde import JsonDoc

import reflex as rx

from .. import app_server, icon_registry
from . import widget_base

__all__ = [
    "Icon",
]


class Icon(widget_base.HtmlWidget):
    icon: str
    _: KW_ONLY
    fill_mode: Literal["fit", "stretch", "tile", "zoom"] = "fit"
    fill: Optional[rx.FillLike] = None

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

    def _custom_serialize(self, server: app_server.AppServer) -> JsonDoc:
        # Get the icon's SVG
        registry = Icon._get_registry()
        svg_source = registry.get_icon_svg(self.icon)

        # Serialize
        return {
            "svgSource": svg_source,
        }


Icon._unique_id = "Icon-builtin"
