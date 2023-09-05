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
    accent_color: rx.Color
    disabled_color: rx.Color

    primary_color_variant: rx.Color
    accent_color_variant: rx.Color
    disabled_color_variant: rx.Color

    # surface colors are often used for backgrounds. Most widgets are placed on
    # top of the surface color.
    background_color: rx.Color
    surface_color: rx.Color
    surface_contrast_color: rx.Color
    surface_active_color: rx.Color

    # Semantic colors express a meaning, such as positive or negative outcomes
    success_color: rx.Color
    warning_color: rx.Color
    danger_color: rx.Color

    success_color_variant: rx.Color
    warning_color_variant: rx.Color
    danger_color_variant: rx.Color

    # Other
    outline_width: float
    corner_radius: float
    base_spacing: float

    # Text styles
    heading_on_primary_style: rx.TextStyle
    subheading_on_primary_style: rx.TextStyle
    text_on_primary_style: rx.TextStyle

    heading_on_accent_style: rx.TextStyle
    subheading_on_accent_style: rx.TextStyle
    text_on_accent_style: rx.TextStyle

    heading_on_surface_style: rx.TextStyle
    subheading_on_surface_style: rx.TextStyle
    text_on_surface_style: rx.TextStyle

    def __init__(
        self,
        *,
        primary_color: Optional[rx.Color] = None,
        accent_color: Optional[rx.Color] = None,
        light: bool = True,
    ) -> None:
        # Impute defaults
        if primary_color is None:
            # Consider "ee3f59"
            primary_color = rx.Color.from_hex("c202ee")

        if accent_color is None:
            accent_color = rx.Color.from_hex("329afc")

        # Main theme colors
        self.primary_color = primary_color
        self.accent_color = accent_color
        self.disabled_color = rx.Color.from_grey(0.5)

        # Create variants for them
        self.primary_color_variant = _make_variant_color(primary_color)
        self.accent_color_variant = _make_variant_color(accent_color)
        self.disabled_color_variant = _make_variant_color(self.disabled_color)

        # Determine the background colors based on whether the theme is light or
        # dark
        if light:
            self.background_color = rx.Color.from_grey(1.0)
            self.surface_color = rx.Color.from_grey(0.98).blend(primary_color, 0.02)
            self.surface_contrast_color = self.surface_color.darker(0.02)
            self.surface_active_color = self.surface_color.blend(primary_color, 0.05)
        else:
            self.background_color = rx.Color.from_grey(0.12)
            self.surface_color = rx.Color.from_grey(0.19).blend(primary_color, 0.02)
            self.surface_contrast_color = self.surface_color.darker(0.06)
            self.surface_active_color = self.surface_color.blend(primary_color, 0.05)

        # Semantic colors
        self.success_color = rx.Color.from_hex("66bb6a")
        self.warning_color = rx.Color.from_hex("f57c00")
        self.danger_color = rx.Color.from_hex("93000a")

        # Create variants for them
        self.success_color_variant = _make_variant_color(self.success_color)
        self.warning_color_variant = _make_variant_color(self.warning_color)
        self.danger_color_variant = _make_variant_color(self.danger_color)

        # Other
        self.outline_width = 0.1
        self.corner_radius = 0.45
        self.base_spacing = 0.5

        # Prepare values which are referenced later
        heading_style = rx.TextStyle(
            font_color=rx.Color.MAGENTA,  # Placeholder, replaced later
            font_size=2.0,
        )
        subheading_style = heading_style.replace(font_size=1.5)
        text_style = heading_style.replace(font_size=1.25)

        font_color_on_primary = primary_color.contrasting(0.8)
        font_color_on_accent = accent_color.contrasting(0.8)
        font_color_on_surface = self.surface_color.contrasting(0.8)

        # Fill in the text styles
        self.heading_on_primary_style = heading_style.replace(
            font_color=font_color_on_primary
        )
        self.subheading_on_primary_style = subheading_style.replace(
            font_color=font_color_on_primary
        )
        self.text_on_primary_style = text_style.replace(
            font_color=font_color_on_primary
        )

        self.heading_on_accent_style = heading_style.replace(
            font_color=font_color_on_accent
        )
        self.subheading_on_accent_style = subheading_style.replace(
            font_color=font_color_on_accent
        )
        self.text_on_accent_style = text_style.replace(font_color=font_color_on_accent)

        self.heading_on_surface_style = heading_style.replace(
            font_color=font_color_on_surface
        )
        self.subheading_on_surface_style = subheading_style.replace(
            font_color=font_color_on_surface
        )
        self.text_on_surface_style = text_style.replace(
            font_color=font_color_on_surface
        )

    def _serialize_colorspec(self, color: color.ColorSpec) -> Jsonable:
        # If the color is a string, just pass it through
        if isinstance(color, str):
            return color

        # If it is a custom color, return it, along with related ones
        return {
            "color": color.rgba,
            "colorVariant": _make_variant_color(color).rgba,
            "textColor": color.contrasting(0.8).rgba,
        }
