from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

import material_color_utilities_python
from typing_extensions import Self
from uniserde import Jsonable

import rio

from . import color

__all__ = [
    "Palette",
    "Theme",
]

# TODO: Consider really noticeable, memorable primary color: #e80265


class TonalPalette:
    def __init__(self, hue: int, chroma: int):
        self._material_palette = material_color_utilities_python.TonalPalette(
            hue, chroma
        )

    def __getitem__(self, tone: int) -> rio.Color:
        return rio.Color._from_material_argb(self._material_palette.tone(tone))


@dataclass(frozen=True)
class Palette:
    background: rio.Color
    background_variant: rio.Color
    background_active: rio.Color

    foreground: rio.Color

    @classmethod
    def _from_color(
        cls,
        color: rio.Color,
        is_light_theme: bool,
    ) -> Self:
        as_hct = material_color_utilities_python.Hct.fromInt(color._as_material_argb)
        hct_palette = TonalPalette(as_hct.hue, as_hct.chroma)

        return Palette(
            background=color,
            background_variant=hct_palette[as_hct.tone + 5],
            background_active=hct_palette[as_hct.tone + 10],
            foreground=hct_palette[10 if as_hct.tone > 50 else 90],
        )


@dataclass(frozen=True)
class Theme:
    """
    Defines the visual style of the application.

    The `Theme` contains all colors, text styles, and other visual properties
    that are used throughout the application. If you wish to change the
    appearance of your app, this is the place to do it.

    TODO: Finalize theming and document it

    TODO: Give an example for how to create a theme and attach it to the
        session.
    """

    _: KW_ONLY

    primary_palette: Palette
    secondary_palette: Palette

    background_palette: Palette
    neutral_palette: Palette

    success_palette: Palette
    warning_palette: Palette
    danger_palette: Palette

    # Other
    corner_radius_small: float
    corner_radius_medium: float
    corner_radius_large: float

    shadow_color: rio.Color

    # Text styles
    heading1_style: rio.TextStyle
    heading2_style: rio.TextStyle
    heading3_style: rio.TextStyle
    text_style: rio.TextStyle

    @classmethod
    def from_color(
        cls,
        primary_color: Optional[rio.Color] = None,
        secondary_color: Optional[rio.Color] = None,
        corner_radius_small: float = 0.6,
        corner_radius_medium: float = 1.6,
        corner_radius_large: float = 2.6,
        light: bool = True,
    ) -> Self:
        # Impute defaults
        if primary_color is None:
            # Consider "ee3f59"
            primary_color = rio.Color.from_hex("c202ee")

        if secondary_color is None:
            secondary_color = rio.Color.from_hex("329afc")

        # Extract palettes from the material theme
        primary_palette = Palette._from_color(primary_color, light)
        secondary_palette = Palette._from_color(secondary_color, light)

        if light:
            background_palette = Palette(
                background=rio.Color.WHITE,
                background_variant=rio.Color.from_grey(0.97).blend(primary_color, 0.03),
                background_active=rio.Color.from_grey(0.97).blend(primary_color, 0.09),
                foreground=rio.Color.from_grey(0.1),
            )

            neutral_palette = Palette(
                background=rio.Color.from_grey(0.97).blend(primary_color, 0.03),
                background_variant=rio.Color.from_grey(0.94).blend(primary_color, 0.03),
                background_active=rio.Color.from_grey(0.94).blend(primary_color, 0.09),
                foreground=rio.Color.from_grey(0.1),
            )

        else:
            background_palette = Palette(
                background=rio.Color.from_grey(0.1),
                background_variant=rio.Color.from_grey(0.2).blend(primary_color, 0.02),
                background_active=rio.Color.from_grey(0.3).blend(primary_color, 0.04),
                foreground=rio.Color.from_grey(0.9),
            )

            neutral_palette = Palette(
                background=rio.Color.from_grey(0.2).blend(primary_color, 0.02),
                background_variant=rio.Color.from_grey(0.3).blend(primary_color, 0.02),
                background_active=rio.Color.from_grey(0.3).blend(primary_color, 0.04),
                foreground=rio.Color.from_grey(0.9),
            )

        success_palette = Palette._from_color(rio.Color.from_hex("1E8E3E"), light)
        warning_palette = Palette._from_color(rio.Color.from_hex("F9A825"), light)
        danger_palette = Palette._from_color(rio.Color.from_hex("B3261E"), light)

        # Text styles
        heading1_style = rio.TextStyle(
            font_size=3.0,
            fill=primary_color,
        )
        heading2_style = heading1_style.replace(font_size=1.8)
        heading3_style = heading1_style.replace(font_size=1.2)
        text_style = heading1_style.replace(
            font_size=1,
            fill=rio.Color.from_grey(0.1 if light else 0.9),
        )

        return cls(
            primary_palette=primary_palette,
            secondary_palette=secondary_palette,
            background_palette=background_palette,
            neutral_palette=neutral_palette,
            success_palette=success_palette,
            warning_palette=warning_palette,
            danger_palette=danger_palette,
            corner_radius_small=corner_radius_small,
            corner_radius_medium=corner_radius_medium,
            corner_radius_large=corner_radius_large,
            shadow_color=rio.Color.from_rgb(0, 0, 0.3, 0.3),
            heading1_style=heading1_style,
            heading2_style=heading2_style,
            heading3_style=heading3_style,
            text_style=text_style,
        )

    def text_color_for(self, color: rio.Color) -> rio.Color:
        """
        Given the color of a background, return which color should be used for
        text on top of it.
        """
        if color.perceived_brightness > 0.5:
            return rio.Color.from_grey(0.1)
        else:
            return rio.Color.from_grey(0.9)

    def _serialize_colorset(self, color: color.ColorSet) -> Jsonable:
        # If the color is a string, just pass it through
        if isinstance(color, str):
            return color

        # If it is a custom color, return it, along with related ones
        return {
            "background": color.rgba,
            "foreground": self.text_color_for(color).rgba,
        }
