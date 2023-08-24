from dataclasses import dataclass

import reflex as rx

__all__ = [
    "Theme",
]


@dataclass(frozen=True)
class Theme:
    # Neutral colors are often used as background, for inactive and unimportant
    # elements
    neutral_color: rx.Color
    neutral_contrast_color: rx.Color
    neutral_active_color: rx.Color

    # The main theme colors. Bright, in your face
    main_color: rx.Color
    accent_color: rx.Color
    active_color: rx.Color

    # Colors to express something, such as positive or negative outcomes
    success_color: rx.Color
    warning_color: rx.Color
    danger_color: rx.Color

    # Line Styles
    outline_width: float

    # Other
    corner_radius: float

    # Animation
    transition_scale: float

    # Text styles
    heading_style: rx.TextStyle
    subheading_style: rx.TextStyle
    sub_subheading_style: rx.TextStyle

    text_style: rx.TextStyle

    @staticmethod
    def light() -> "Theme":
        raise NotImplementedError("TODO: Implement light default theme")

    @staticmethod
    def dark(
        *,
        neutral_color=rx.Color.from_hex("36393b"),
        main_color=rx.Color.from_hex("ff785a"),
        accent_color=rx.Color.from_hex("b4e1ff"),
    ) -> "Theme":
        text_style = rx.TextStyle(
            font_color=neutral_color.contrasting(0.9),
        )
        active_color = main_color.brighter(0.15)

        return Theme(
            # Neutral colors
            neutral_color=neutral_color,
            neutral_contrast_color=neutral_color.darker(0.05),
            neutral_active_color=neutral_color.blend(active_color, 0.07),
            # Main theme colors
            main_color=main_color,
            accent_color=accent_color,
            active_color=active_color,
            # Expressive colors
            success_color=rx.Color.from_hex("0AFF61"),
            warning_color=rx.Color.from_hex("ffaa5a"),
            danger_color=rx.Color.from_hex("D42C24"),
            # Line styles
            outline_width=0.1,
            # Other
            corner_radius=0.45,
            # Animation
            transition_scale=1.0,
            # Text styles
            heading_style=text_style.replace(font_size=2.0),
            subheading_style=text_style.replace(font_size=1.5),
            sub_subheading_style=text_style.replace(font_size=1.25),
            text_style=text_style,
        )
