from __future__ import annotations

import functools
from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from typing_extensions import Self
from uniserde import Jsonable

import rio

from . import color

# This module imports `curses` even though it doesn't need it, which causes
# problems on Windows. Since it's unused, we'll just give it a fake module if
# the real curses isn't available.
try:
    import material_color_utilities_python
except ImportError:
    import sys
    import types

    sys.modules["curses"] = types.SimpleNamespace(termattrs=None)  # type: ignore
    import material_color_utilities_python

    del sys.modules["curses"]


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

        return cls(
            background=color,
            background_variant=hct_palette[as_hct.tone + 5],
            background_active=hct_palette[as_hct.tone + 15],
            foreground=hct_palette[8 if as_hct.tone > 50 else 92],
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
    disabled_palette: Palette

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
        neutral_color: Optional[rio.Color] = None,
        success_color: Optional[rio.Color] = None,
        warning_color: Optional[rio.Color] = None,
        danger_color: Optional[rio.Color] = None,
        corner_radius_small: float = 0.6,
        corner_radius_medium: float = 1.6,
        corner_radius_large: float = 2.6,
        light: bool = True,
    ) -> Self:
        # Impute defaults
        if primary_color is None:
            primary_color = rio.Color.from_hex("b002ef")

        if secondary_color is None:
            secondary_color = rio.Color.from_hex("329afc")

        # Extract palettes from the material theme
        primary_palette = Palette._from_color(primary_color, light)
        secondary_palette = Palette._from_color(secondary_color, light)

        if light:
            background_palette = Palette(
                background=rio.Color.WHITE,
                background_variant=rio.Color.from_grey(0.96).blend(primary_color, 0.04),
                background_active=rio.Color.from_grey(0.96).blend(primary_color, 0.15),
                foreground=rio.Color.from_grey(0.15),
            )

            if neutral_color is None:
                neutral_palette = Palette(
                    background=rio.Color.from_grey(0.97).blend(primary_color, 0.04),
                    background_variant=rio.Color.from_grey(0.93).blend(
                        primary_color, 0.07
                    ),
                    background_active=rio.Color.from_grey(0.93).blend(
                        primary_color, 0.15
                    ),
                    foreground=rio.Color.from_grey(0.1),
                )
            else:
                neutral_palette = Palette._from_color(neutral_color, light)

            disabled_palette = Palette(
                rio.Color.from_grey(0.7),
                rio.Color.from_grey(0.75),
                rio.Color.from_grey(0.80),
                rio.Color.from_grey(0.4),
            )

            shadow_color = rio.Color.from_rgb(0.1, 0.1, 0.4, 0.3)

        else:
            background_palette = Palette(
                background=rio.Color.from_grey(0.08).blend(primary_color, 0.02),
                background_variant=rio.Color.from_grey(0.14).blend(primary_color, 0.04),
                background_active=rio.Color.from_grey(0.14).blend(primary_color, 0.10),
                foreground=rio.Color.from_grey(0.9),
            )

            if neutral_color is None:
                neutral_palette = Palette(
                    background=rio.Color.from_grey(0.16).blend(primary_color, 0.03),
                    background_variant=rio.Color.from_grey(0.2).blend(
                        primary_color, 0.04
                    ),
                    background_active=rio.Color.from_grey(0.2).blend(
                        primary_color, 0.10
                    ),
                    foreground=rio.Color.from_grey(0.5),
                )
            else:
                neutral_palette = Palette._from_color(neutral_color, light)

            disabled_palette = Palette(
                rio.Color.from_grey(0.2),
                rio.Color.from_grey(0.15),
                rio.Color.from_grey(0.10),
                rio.Color.from_grey(0.6),
            )

            shadow_color = rio.Color.from_rgb(0.0, 0.0, 0.1, 0.35)

        # Semantic colors
        if success_color is None:
            success_color = rio.Color.from_hex("1E8E3E")

        if warning_color is None:
            warning_color = rio.Color.from_hex("F9A825")

        if danger_color is None:
            danger_color = rio.Color.from_hex("B3261E")

        success_palette = Palette._from_color(success_color, light)
        warning_palette = Palette._from_color(warning_color, light)
        danger_palette = Palette._from_color(danger_color, light)

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
            disabled_palette=disabled_palette,
            success_palette=success_palette,
            warning_palette=warning_palette,
            danger_palette=danger_palette,
            corner_radius_small=corner_radius_small,
            corner_radius_medium=corner_radius_medium,
            corner_radius_large=corner_radius_large,
            shadow_color=shadow_color,
            heading1_style=heading1_style,
            heading2_style=heading2_style,
            heading3_style=heading3_style,
            text_style=text_style,
        )

    @classmethod
    def pair_from_color(
        cls,
        *,
        primary_color: Optional[rio.Color] = None,
        secondary_color: Optional[rio.Color] = None,
        success_color: Optional[rio.Color] = None,
        warning_color: Optional[rio.Color] = None,
        danger_color: Optional[rio.Color] = None,
        corner_radius_small: float = 0.6,
        corner_radius_medium: float = 1.6,
        corner_radius_large: float = 2.6,
    ) -> Tuple[Self, Self]:
        func = functools.partial(
            cls.from_color,
            primary_color=primary_color,
            secondary_color=secondary_color,
            success_color=success_color,
            warning_color=warning_color,
            danger_color=danger_color,
            corner_radius_small=corner_radius_small,
            corner_radius_medium=corner_radius_medium,
            corner_radius_large=corner_radius_large,
        )
        return (
            func(light=True),
            func(light=False),
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
