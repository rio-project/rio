from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import Jsonable

import reflex as rx

from . import color

__all__ = [
    "Theme",
]

# TODO: Consider really noticeable, memorable primary color: #e80265


def _make_variant_color(base: rx.Color) -> rx.Color:
    return rx.Color.from_hsv(
        base.hue,
        base.saturation * 0.5,
        min(base.value * 1.5, 1),
    )


class Theme:
    _: KW_ONLY

    # The main theme colors
    primary_color: rx.Color
    secondary_color: rx.Color
    disabled_color: rx.Color

    primary_color_variant: rx.Color
    secondary_color_variant: rx.Color
    disabled_color_variant: rx.Color

    # Surface colors are often used for backgrounds. Most widgets are placed on
    # top of the surface color.
    background_color: rx.Color
    surface_color: rx.Color
    surface_color_variant: rx.Color
    surface_active_color: rx.Color

    # Semantic colors express a meaning, such as positive or negative outcomes
    success_color: rx.Color
    warning_color: rx.Color
    danger_color: rx.Color

    success_color_variant: rx.Color
    warning_color_variant: rx.Color
    danger_color_variant: rx.Color

    # Other
    corner_radius_small: float
    base_spacing: float
    shadow_radius: float
    shadow_color: rx.Color

    # Text styles
    heading1_style: rx.TextStyle
    heading2_style: rx.TextStyle
    heading2_style: rx.TextStyle
    text_style: rx.TextStyle

    heading_on_primary_color: rx.Color
    text_on_primary_color: rx.Color

    heading_on_secondary_color: rx.Color
    text_on_secondary_color: rx.Color

    text_color_on_light: rx.Color
    text_color_on_dark: rx.Color

    def __init__(
        self,
        *,
        primary_color: Optional[rx.Color] = None,
        secondary_color: Optional[rx.Color] = None,
        success_color: Optional[rx.Color] = None,
        warning_color: Optional[rx.Color] = None,
        danger_color: Optional[rx.Color] = None,
        corner_radius_small: float = 0.6,
        corner_radius_large: float = 3.0,
        base_spacing: float = 0.5,
        light: bool = True,
    ) -> None:
        # Impute defaults
        if primary_color is None:
            # Consider "ee3f59"
            primary_color = rx.Color.from_hex("c202ee")

        if secondary_color is None:
            secondary_color = rx.Color.from_hex("329afc")

        # Main theme colors
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.disabled_color = rx.Color.from_grey(0.6 if light else 0.3)

        # Create variants for them
        self.primary_color_variant = _make_variant_color(primary_color)
        self.secondary_color_variant = _make_variant_color(secondary_color)
        self.disabled_color_variant = _make_variant_color(self.disabled_color)

        # Determine the background colors based on whether the theme is light or
        # dark
        if light:
            self.background_color = rx.Color.from_grey(1.0)
            self.surface_color = rx.Color.from_grey(0.98).blend(primary_color, 0.03)
            self.surface_color_variant = self.surface_color.darker(0.02)
            self.surface_active_color = self.surface_color.blend(primary_color, 0.06)
        else:
            self.background_color = rx.Color.from_grey(0.12)
            self.surface_color = rx.Color.from_grey(0.19).blend(primary_color, 0.03)
            self.surface_color_variant = self.surface_color.darker(0.06)
            self.surface_active_color = self.surface_color.blend(primary_color, 0.06)

        # Semantic colors
        if success_color is None:
            self.success_color = rx.Color.from_hex("66bb6a")
        else:
            self.success_color = success_color

        if warning_color is None:
            self.warning_color = rx.Color.from_hex("f57c00")
        else:
            self.warning_color = warning_color

        if danger_color is None:
            self.danger_color = rx.Color.from_hex("93000a")
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
        self.shadow_color = rx.Color.BLACK.replace(opacity=0.5)
        self.shadow_radius = 1

        # Text styles

        # These are filled out first, so the remaining colors may access them
        # via `self._text_color_for`.
        self.text_color_on_light = rx.Color.from_grey(0.1)
        self.text_color_on_dark = rx.Color.from_grey(0.9)

        self.heading1_style = rx.TextStyle(
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

    def text_color_for(self, color: rx.Color) -> rx.Color:
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
