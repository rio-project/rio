from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from uniserde import Jsonable

import rio

from . import color

__all__ = [
    "Theme",
]

# TODO: Consider really noticeable, memorable primary color: #e80265


def _make_variant_color(base: rio.Color) -> rio.Color:
    return rio.Color.from_hsv(
        base.hue,
        base.saturation * 0.5,
        min(base.value * 1.5, 1),
    )


class Theme:
    _: KW_ONLY

    # The main theme colors
    primary_color: rio.Color
    secondary_color: rio.Color
    disabled_color: rio.Color

    primary_color_variant: rio.Color
    secondary_color_variant: rio.Color
    disabled_color_variant: rio.Color

    # Surface colors are often used for backgrounds. Most widgets are placed on
    # top of the surface color.
    background_color: rio.Color
    surface_color: rio.Color
    surface_color_variant: rio.Color
    surface_active_color: rio.Color

    # Semantic colors express a meaning, such as positive or negative outcomes
    success_color: rio.Color
    warning_color: rio.Color
    danger_color: rio.Color

    success_color_variant: rio.Color
    warning_color_variant: rio.Color
    danger_color_variant: rio.Color

    # Other
    corner_radius_small: float
    base_spacing: float
    shadow_radius: float
    shadow_color: rio.Color

    # Text styles
    heading1_style: rio.TextStyle
    heading2_style: rio.TextStyle
    heading2_style: rio.TextStyle
    text_style: rio.TextStyle

    heading_on_primary_color: rio.Color
    text_on_primary_color: rio.Color

    heading_on_secondary_color: rio.Color
    text_on_secondary_color: rio.Color

    text_color_on_light: rio.Color
    text_color_on_dark: rio.Color

    def __init__(
        self,
        *,
        primary_color: Optional[rio.Color] = None,
        secondary_color: Optional[rio.Color] = None,
        success_color: Optional[rio.Color] = None,
        warning_color: Optional[rio.Color] = None,
        danger_color: Optional[rio.Color] = None,
        corner_radius_small: float = 0.6,
        corner_radius_large: float = 2.5,
        base_spacing: float = 0.5,
        light: bool = True,
    ) -> None:
        # Impute defaults
        if primary_color is None:
            # Consider "ee3f59"
            primary_color = rio.Color.from_hex("c202ee")

        if secondary_color is None:
            secondary_color = rio.Color.from_hex("329afc")

        # Main theme colors
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.disabled_color = rio.Color.from_grey(0.6 if light else 0.3)

        # Create variants for them
        self.primary_color_variant = _make_variant_color(primary_color)
        self.secondary_color_variant = _make_variant_color(secondary_color)
        self.disabled_color_variant = _make_variant_color(self.disabled_color)

        # Determine the background colors based on whether the theme is light or
        # dark
        if light:
            self.background_color = rio.Color.from_grey(1.0)
            self.surface_color = rio.Color.from_grey(0.98).blend(primary_color, 0.03)
            self.surface_color_variant = self.surface_color.darker(0.02)
            self.surface_active_color = self.surface_color.blend(primary_color, 0.06)
        else:
            self.background_color = rio.Color.from_grey(0.12)
            self.surface_color = rio.Color.from_grey(0.19).blend(primary_color, 0.025)
            self.surface_color_variant = self.surface_color.darker(0.06)
            self.surface_active_color = self.surface_color.blend(primary_color, 0.05)

        # Semantic colors
        if success_color is None:
            self.success_color = rio.Color.from_hex("66bb6a")
        else:
            self.success_color = success_color

        if warning_color is None:
            self.warning_color = rio.Color.from_hex("f57c00")
        else:
            self.warning_color = warning_color

        if danger_color is None:
            self.danger_color = rio.Color.from_hex("93000a")
        else:
            self.danger_color = danger_color

        # Create variants for them
        self.success_color_variant = _make_variant_color(self.success_color)
        self.warning_color_variant = _make_variant_color(self.warning_color)
        self.danger_color_variant = _make_variant_color(self.danger_color)

        # Other
        self.corner_radius_small = corner_radius_small
        self.corner_radius_large = corner_radius_large
        self.base_spacing = base_spacing
        self.shadow_color = rio.Color.BLACK.replace(opacity=0.5)
        self.shadow_radius = 1

        # Text styles

        # These are filled out first, so the remaining colors may access them
        # via `self._text_color_for`.
        self.text_color_on_light = rio.Color.from_grey(0.1)
        self.text_color_on_dark = rio.Color.from_grey(0.9)

        self.heading1_style = rio.TextStyle(
            font_size=3.0,
            font_color=self.primary_color,
        )
        self.heading2_style = self.heading1_style.replace(font_size=2.0)
        self.heading3_style = self.heading1_style.replace(font_size=1.5)
        self.text_style = self.heading1_style.replace(
            font_size=1,
            font_color=self.text_color_for(self.surface_color),
        )

        self.heading_on_primary_color = self.secondary_color
        self.text_on_primary_color = self.secondary_color

        self.heading_on_secondary_color = self.primary_color
        self.text_on_secondary_color = self.primary_color

    def text_color_for(self, color: rio.Color) -> rio.Color:
        """
        Given the color of a background, return which color should be used for
        text on top of it.
        """
        if color.perceived_brightness > 0.5:
            return self.text_color_on_light
        else:
            return self.text_color_on_dark

    def _serialize_colorset(self, color: color.ColorSet) -> Jsonable:
        # If the color is a string, just pass it through
        if isinstance(color, str):
            return color

        # If it is a custom color, return it, along with related ones
        return {
            "color": color.rgba,
            "colorVariant": _make_variant_color(color).rgba,
            "textColor": self.text_color_for(color).rgba,
        }
