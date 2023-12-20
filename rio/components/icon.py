from __future__ import annotations

from dataclasses import KW_ONLY
from pathlib import Path
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .. import color, fills, icon_registry
from . import component_base

__all__ = [
    "Icon",
]


class Icon(component_base.FundamentalComponent):
    """
    Displays one of many pre-bundled icons.

    Icons are a great way to add polish to your app. A good icon can help your
    users understand your app and immediately recognize what a component does.

    Rio includes hundreds of free icons, allowing you to easily add them to your
    app without having to find or create your own. The `Icon` component displays
    one of these icons.

    Note that unlike most components in Rio, `Icon` does not have a `natural`
    size, they can be easily be scaled to fit any size. Therefore it defaults to
    a width and height of 1.3, which is a great size when mixing icons with
    text.

    Icon names are in the format `set_name/icon_name:variant`. Rio already ships
    with the `material` icon set, which contains icons in the style of Google's
    Material Design. You can browse all available icons on [the Rio website](
    https://todo.com/icons).  # TODO: Add actual link

    The set name and variant can be omitted. If no set name is specified, it
    defaults to `material`. If not variant is specified, the default version of
    the icon, i.e. no variant, is used.

    Attributes:
        icon: The name of the icon to display, in the format
            `icon-set/name:variant`. You can browse all available icons on [the
            Rio website](https://todo.com/icons).  # TODO: Add actual link

        fill: The color scheme of the icon. The text color is used if no fill is
            specified.
    """

    icon: str
    _: KW_ONLY
    fill: Union[rio.FillLike, color.ColorSet, Literal["dim"]]

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
        accessed as `icon_name`, `set_name/icon_name` or
        `set_name/icon_name:variant`.

        There must not already be a set with the given name.

        The icon set is a zip archive containing SVG files. The SVG files must
        have a `viewBox` attribute, but no height or width. They will be colored
        by the `fill` property of the `Icon` component.

        Files located in the root of the archive can be accessed as
        `set_name/icon_name`. Files located in a subdirectory can be accessed as
        `set_name/icon_name:variant`.

        Args:
            set_name: The name of the new icon set. This will be used to access
                the icons.

            icon_set_zip_path: The path to the zip archive containing the icon
                set.
        """
        registry = Icon._get_registry()

        if set_name in registry.icon_set_archives:
            raise ValueError(f"There is already an icon set named `{set_name}`")

        registry.icon_set_archives[set_name] = icon_set_zip_path

    def __init__(
        self,
        icon: str,
        *,
        fill: Union[rio.FillLike, color.ColorSet, Literal["dim"]] = "keep",
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["grow"], float] = 1.3,
        height: Union[Literal["grow"], float] = 1.3,
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        super().__init__(
            key=key,
            margin=margin,
            margin_x=margin_x,
            margin_y=margin_y,
            margin_left=margin_left,
            margin_top=margin_top,
            margin_right=margin_right,
            margin_bottom=margin_bottom,
            width=width,
            height=height,
            align_x=align_x,
            align_y=align_y,
        )

        self.icon = icon
        self.fill = fill

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

        # Serialize
        return {
            "svgSource": svg_source,
            "fill": fill,
        }


Icon._unique_id = "Icon-builtin"
