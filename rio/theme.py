from __future__ import annotations

import functools
from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from typing_extensions import Self
from uniserde import Jsonable

import rio

from . import color
from .text_style import ROBOTO, ROBOTO_MONO

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

T = TypeVar("T")


def elvis(optional: Optional[T], default: T) -> T:
    if optional is None:
        return default
    else:
        return optional


class MaterialPalette:
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
    def from_color(
        cls,
        color: rio.Color,
        is_light_theme: bool,
    ) -> Self:
        as_hct = material_color_utilities_python.Hct.fromInt(color._as_material_argb)
        hct_palette = MaterialPalette(as_hct.hue, as_hct.chroma)

        return cls(
            background=color,
            background_variant=hct_palette[as_hct.tone + 5],
            background_active=hct_palette[as_hct.tone + 15],
            foreground=hct_palette[8 if as_hct.tone > 60 else 92],
        )

    def replace(
        self,
        background: rio.Color | None = None,
        background_variant: rio.Color | None = None,
        background_active: rio.Color | None = None,
        foreground: rio.Color | None = None,
    ) -> Palette:
        return Palette(
            background=elvis(background, self.background),
            background_variant=elvis(background_variant, self.background_variant),
            background_active=elvis(background_active, self.background_active),
            foreground=elvis(foreground, self.foreground),
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
    hud_palette: Palette
    disabled_palette: Palette

    success_palette: Palette
    warning_palette: Palette
    danger_palette: Palette

    # Other
    corner_radius_small: float
    corner_radius_medium: float
    corner_radius_large: float

    shadow_color: rio.Color

    font: rio.Font
    monospace_font: rio.Font

    # Text styles
    heading1_style: rio.TextStyle
    heading2_style: rio.TextStyle
    heading3_style: rio.TextStyle
    text_style: rio.TextStyle

    @classmethod
    def from_color(
        cls,
        primary_color: rio.Color | None = None,
        secondary_color: rio.Color | None = None,
        background_color: rio.Color | None = None,
        neutral_color: rio.Color | None = None,
        hud_color: rio.Color | None = None,
        disabled_color: rio.Color | None = None,
        success_color: rio.Color | None = None,
        warning_color: rio.Color | None = None,
        danger_color: rio.Color | None = None,
        corner_radius_small: float = 0.5,
        corner_radius_medium: float = 1.4,
        corner_radius_large: float = 2.4,
        color_headings: bool | Literal["auto"] = "auto",
        font: rio.Font = ROBOTO,
        monospace_font: rio.Font = ROBOTO_MONO,
        light: bool = True,
    ) -> Self:
        # Impute defaults
        if primary_color is None:
            primary_color = rio.Color.from_hex("b002ef")

        if secondary_color is None:
            secondary_color = rio.Color.from_hex("329afc")

        if success_color is None:
            success_color = rio.Color.from_hex("1E8E3E")

        if warning_color is None:
            warning_color = rio.Color.from_hex("F9A825")

        if danger_color is None:
            danger_color = rio.Color.from_hex("B3261E")

        # Extract palettes from the material theme
        primary_palette = Palette.from_color(primary_color, light)
        secondary_palette = Palette.from_color(secondary_color, light)

        if light:
            if background_color is None:
                background_palette = Palette(
                    background=rio.Color.WHITE,
                    background_variant=rio.Color.from_grey(0.96).blend(
                        primary_color, 0.04
                    ),
                    background_active=rio.Color.from_grey(0.96).blend(
                        primary_color, 0.1
                    ),
                    foreground=rio.Color.from_grey(0.15),
                )
            else:
                background_palette = Palette.from_color(background_color, light)

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
                neutral_palette = Palette.from_color(neutral_color, light)

            if hud_color is None:
                hud_palette = Palette.from_color(
                    rio.Color.from_grey(
                        0.06,
                        opacity=0.9,
                    ),
                    light,
                )
            else:
                hud_palette = Palette.from_color(hud_color, light)

            if disabled_color is None:
                disabled_palette = Palette(
                    rio.Color.from_grey(0.7),
                    rio.Color.from_grey(0.75),
                    rio.Color.from_grey(0.80),
                    rio.Color.from_grey(0.4),
                )
            else:
                disabled_palette = Palette.from_color(disabled_color, light)

            shadow_color = rio.Color.from_rgb(0.1, 0.1, 0.4, 0.3)

        else:
            if background_color is None:
                background_palette = Palette(
                    background=rio.Color.from_grey(0.08).blend(primary_color, 0.02),
                    background_variant=rio.Color.from_grey(0.14).blend(
                        primary_color, 0.04
                    ),
                    background_active=rio.Color.from_grey(0.14).blend(
                        primary_color, 0.10
                    ),
                    foreground=rio.Color.from_grey(0.9),
                )
            else:
                background_palette = Palette.from_color(background_color, light)

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
                neutral_palette = Palette.from_color(neutral_color, light)

            if hud_color is None:
                hud_palette = Palette.from_color(
                    rio.Color.from_grey(
                        0.2,
                        opacity=0.8,
                    ),
                    light,
                )
            else:
                hud_palette = Palette.from_color(hud_color, light)

            if disabled_color is None:
                disabled_palette = Palette(
                    rio.Color.from_grey(0.2),
                    rio.Color.from_grey(0.15),
                    rio.Color.from_grey(0.10),
                    rio.Color.from_grey(0.6),
                )
            else:
                disabled_palette = Palette.from_color(disabled_color, light)

            shadow_color = rio.Color.from_rgb(0.0, 0.0, 0.1, 0.35)

        # Semantic colors
        success_palette = Palette.from_color(success_color, light)
        warning_palette = Palette.from_color(warning_color, light)
        danger_palette = Palette.from_color(danger_color, light)

        # Colorful headings can be a problem when the primary color is similar
        # to the background/neutral color. If the `color_headings` argument is
        # set to `auto`, disable coloring if the colors are close.
        if color_headings == "auto":
            brightness1 = primary_palette.background.perceived_brightness
            brightness2 = background_palette.background.perceived_brightness

            color_headings = abs(brightness1 - brightness2) > 0.3

        # Text styles
        text_color = rio.Color.from_grey(0.1 if light else 0.9)

        heading1_style = rio.TextStyle(
            font_size=3.0,
            fill=primary_color if color_headings else text_color,
        )
        heading2_style = heading1_style.replace(font_size=1.8)
        heading3_style = heading1_style.replace(font_size=1.2)
        text_style = heading1_style.replace(
            font_size=1,
            fill=text_color,
        )

        return cls(
            primary_palette=primary_palette,
            secondary_palette=secondary_palette,
            background_palette=background_palette,
            neutral_palette=neutral_palette,
            hud_palette=hud_palette,
            disabled_palette=disabled_palette,
            success_palette=success_palette,
            warning_palette=warning_palette,
            danger_palette=danger_palette,
            corner_radius_small=corner_radius_small,
            corner_radius_medium=corner_radius_medium,
            corner_radius_large=corner_radius_large,
            shadow_color=shadow_color,
            font=font,
            monospace_font=monospace_font,
            heading1_style=heading1_style,
            heading2_style=heading2_style,
            heading3_style=heading3_style,
            text_style=text_style,
        )

    @classmethod
    def pair_from_color(
        cls,
        *,
        primary_color: rio.Color | None = None,
        secondary_color: rio.Color | None = None,
        background_color: rio.Color | None = None,
        neutral_color: rio.Color | None = None,
        hud_color: rio.Color | None = None,
        disabled_color: rio.Color | None = None,
        success_color: rio.Color | None = None,
        warning_color: rio.Color | None = None,
        danger_color: rio.Color | None = None,
        corner_radius_small: float = 0.6,
        corner_radius_medium: float = 1.6,
        corner_radius_large: float = 2.6,
        font: rio.Font = ROBOTO,
        monospace_font: rio.Font = ROBOTO_MONO,
        color_headings: bool | Literal["auto"] = "auto",
    ) -> tuple[Self, Self]:
        func = functools.partial(
            cls.from_color,
            primary_color=primary_color,
            secondary_color=secondary_color,
            background_color=background_color,
            neutral_color=neutral_color,
            hud_color=hud_color,
            disabled_color=disabled_color,
            success_color=success_color,
            warning_color=warning_color,
            danger_color=danger_color,
            corner_radius_small=corner_radius_small,
            corner_radius_medium=corner_radius_medium,
            corner_radius_large=corner_radius_large,
            font=font,
            monospace_font=monospace_font,
            color_headings=color_headings,
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
        if color.perceived_brightness > 0.6:
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

    def replace(
        self,
        primary_palette: Palette | None = None,
        secondary_palette: Palette | None = None,
        background_palette: Palette | None = None,
        neutral_palette: Palette | None = None,
        hud_palette: Palette | None = None,
        disabled_palette: Palette | None = None,
        success_palette: Palette | None = None,
        warning_palette: Palette | None = None,
        danger_palette: Palette | None = None,
        corner_radius_small: float | None = None,
        corner_radius_medium: float | None = None,
        corner_radius_large: float | None = None,
        shadow_color: rio.Color | None = None,
        font_family: rio.Font | None = None,
        monospace_font: rio.Font | None = None,
        heading1_style: rio.TextStyle | None = None,
        heading2_style: rio.TextStyle | None = None,
        heading3_style: rio.TextStyle | None = None,
        text_style: rio.TextStyle | None = None,
    ) -> Theme:
        return Theme(
            primary_palette=elvis(primary_palette, self.primary_palette),
            secondary_palette=elvis(secondary_palette, self.secondary_palette),
            background_palette=elvis(background_palette, self.background_palette),
            neutral_palette=elvis(neutral_palette, self.neutral_palette),
            hud_palette=elvis(hud_palette, self.hud_palette),
            disabled_palette=elvis(disabled_palette, self.disabled_palette),
            success_palette=elvis(success_palette, self.success_palette),
            warning_palette=elvis(warning_palette, self.warning_palette),
            danger_palette=elvis(danger_palette, self.danger_palette),
            corner_radius_small=elvis(corner_radius_small, self.corner_radius_small),
            corner_radius_medium=elvis(corner_radius_medium, self.corner_radius_medium),
            corner_radius_large=elvis(corner_radius_large, self.corner_radius_large),
            shadow_color=elvis(shadow_color, self.shadow_color),
            font=elvis(font_family, self.font),
            monospace_font=elvis(monospace_font, self.monospace_font),
            heading1_style=elvis(heading1_style, self.heading1_style),
            heading2_style=elvis(heading2_style, self.heading2_style),
            heading3_style=elvis(heading3_style, self.heading3_style),
            text_style=elvis(text_style, self.text_style),
        )

    @property
    def is_light_theme(self) -> bool:
        return self.primary_palette.background.perceived_brightness >= 0.5

    @property
    def primary_color(self) -> rio.Color:
        return self.primary_palette.background

    @property
    def secondary_color(self) -> rio.Color:
        return self.secondary_palette.background

    @property
    def background_color(self) -> rio.Color:
        return self.background_palette.background

    @property
    def neutral_color(self) -> rio.Color:
        return self.neutral_palette.background

    @property
    def hud_color(self) -> rio.Color:
        return self.hud_palette.background

    @property
    def disabled_color(self) -> rio.Color:
        return self.disabled_palette.background

    @property
    def success_color(self) -> rio.Color:
        return self.success_palette.background

    @property
    def warning_color(self) -> rio.Color:
        return self.warning_palette.background

    @property
    def danger_color(self) -> rio.Color:
        return self.danger_palette.background
