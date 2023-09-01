from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

import reflex as rx

from . import color

__all__ = [
    "Theme",
]


@dataclass(frozen=True)
class Theme:
    _: KW_ONLY

    # The main theme colors. Bright, in your face
    primary_color: rx.Color
    accent_color: rx.Color

    # Neutral colors are often used as background, for inactive and unimportant
    # elements
    neutral_color: rx.Color
    neutral_contrast_color: rx.Color
    neutral_active_color: rx.Color

    # Semantic colors express a meaning, such as positive or negative outcomes
    success_color: rx.Color
    warning_color: rx.Color
    danger_color: rx.Color

    # Other
    outline_width: float
    corner_radius: float
    base_spacing: float

    # Animation
    animation_speed: float

    # Text styles
    heading_on_primary_color_style: rx.TextStyle
    subheading_on_primary_color_style: rx.TextStyle
    text_on_primary_color_style: rx.TextStyle

    heading_on_accent_color_style: rx.TextStyle
    subheading_on_accent_color_style: rx.TextStyle
    text_on_accent_color_style: rx.TextStyle

    heading_on_neutral_color_style: rx.TextStyle
    subheading_on_neutral_color_style: rx.TextStyle
    text_on_neutral_color_style: rx.TextStyle

    @staticmethod
    def light(
        *,
        neutral_color: Optional[rx.Color] = None,
        primary_color: Optional[rx.Color] = None,
        accent_color: Optional[rx.Color] = None,
    ) -> "Theme":
        # Impute defaults
        if neutral_color is None:
            neutral_color = rx.Color.from_hex("ffffff")

        if primary_color is None:
            primary_color = rx.Color.from_hex("#c202ee")

        if accent_color is None:
            accent_color = rx.Color.from_hex("ee3f59")

        # Prepare values which are referenced later
        heading_style = rx.TextStyle(
            font_color=neutral_color.contrasting(0.8),
            font_size=2.0,
        )
        subheading_style = heading_style.replace(font_size=1.5)
        text_style = heading_style.replace(font_size=1.25)

        font_color_on_primary = primary_color.contrasting(0.8)
        font_color_on_accent = accent_color.contrasting(0.8)
        font_color_on_neutral = neutral_color.contrasting(0.8)

        return Theme(
            # Main theme colors
            primary_color=primary_color,
            accent_color=accent_color,
            # Neutral colors
            neutral_color=neutral_color,
            neutral_contrast_color=neutral_color.darker(0.03).blend(
                primary_color, 0.02
            ),
            neutral_active_color=neutral_color.blend(primary_color, 0.02),
            # Semantic colors
            success_color=rx.Color.from_hex("0AFF61"),
            warning_color=rx.Color.from_hex("ffaa5a"),
            danger_color=rx.Color.from_hex("D42C24"),
            # Line styles
            outline_width=0.1,
            base_spacing=0.5,
            corner_radius=0.45,
            # Animation
            animation_speed=1.0,
            # Text styles (On primary)
            heading_on_primary_color_style=heading_style.replace(
                font_color=font_color_on_primary
            ),
            subheading_on_primary_color_style=subheading_style.replace(
                font_color=font_color_on_primary
            ),
            text_on_primary_color_style=text_style.replace(
                font_color=font_color_on_primary
            ),
            # Text styles (On accent)
            heading_on_accent_color_style=heading_style.replace(
                font_color=font_color_on_accent
            ),
            subheading_on_accent_color_style=subheading_style.replace(
                font_color=font_color_on_accent
            ),
            text_on_accent_color_style=text_style.replace(
                font_color=font_color_on_accent
            ),
            # Text styles (On neutral)
            heading_on_neutral_color_style=heading_style.replace(
                font_color=font_color_on_neutral
            ),
            subheading_on_neutral_color_style=subheading_style.replace(
                font_color=font_color_on_neutral
            ),
            text_on_neutral_color_style=text_style.replace(
                font_color=font_color_on_neutral
            ),
        )

    @staticmethod
    def dark(
        *,
        neutral_color: Optional[rx.Color] = None,
        primary_color: Optional[rx.Color] = None,
        accent_color: Optional[rx.Color] = None,
    ) -> "Theme":
        # Impute defaults
        if neutral_color is None:
            neutral_color = rx.Color.from_hex("1f1f1f")

        if primary_color is None:
            primary_color = rx.Color.from_hex("#c202ee")

        if accent_color is None:
            accent_color = rx.Color.from_hex("ee3f59")

        # Prepare values which are referenced later
        heading_style = rx.TextStyle(
            font_color=neutral_color.contrasting(0.8),
            font_size=2.0,
        )
        subheading_style = heading_style.replace(font_size=1.5)
        text_style = heading_style.replace(font_size=1.25)

        font_color_on_primary = primary_color.contrasting(0.8)
        font_color_on_accent = accent_color.contrasting(0.8)
        font_color_on_neutral = neutral_color.contrasting(0.8)

        return Theme(
            # Main theme colors
            primary_color=primary_color,
            accent_color=accent_color,
            # Neutral colors
            neutral_color=neutral_color,
            neutral_contrast_color=neutral_color.brighter(0.05),
            neutral_active_color=neutral_color.blend(primary_color, 0.02),
            # Semantic colors
            success_color=rx.Color.from_hex("0AFF61"),
            warning_color=rx.Color.from_hex("ffaa5a"),
            danger_color=rx.Color.from_hex("D42C24"),
            # Line styles
            outline_width=0.1,
            base_spacing=0.5,
            corner_radius=0.45,
            # Animation
            animation_speed=1.0,
            # Text styles (On primary)
            heading_on_primary_color_style=heading_style.replace(
                font_color=font_color_on_primary
            ),
            subheading_on_primary_color_style=subheading_style.replace(
                font_color=font_color_on_primary
            ),
            text_on_primary_color_style=text_style.replace(
                font_color=font_color_on_primary
            ),
            # Text styles (On accent)
            heading_on_accent_color_style=heading_style.replace(
                font_color=font_color_on_accent
            ),
            subheading_on_accent_color_style=subheading_style.replace(
                font_color=font_color_on_accent
            ),
            text_on_accent_color_style=text_style.replace(
                font_color=font_color_on_accent
            ),
            # Text styles (On neutral)
            heading_on_neutral_color_style=heading_style.replace(
                font_color=font_color_on_neutral
            ),
            subheading_on_neutral_color_style=subheading_style.replace(
                font_color=font_color_on_neutral
            ),
            text_on_neutral_color_style=text_style.replace(
                font_color=font_color_on_neutral
            ),
        )
