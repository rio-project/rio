from pathlib import Path
from typing import *  # type: ignore

import reflex as rx

from .. import components as comps
from .. import theme


def make_slideshow_placeholder(variant: int) -> rx.Widget:
    colors = [
        rx.Color.RED,
        rx.Color.GREEN,
        rx.Color.BLUE,
        rx.Color.YELLOW,
        rx.Color.PURPLE,
        rx.Color.MAGENTA,
    ]

    return rx.Rectangle(
        child=rx.Text(
            f"Slideshow Page {variant}",
        ),
        style=rx.BoxStyle(
            fill=colors[variant % len(colors)],
        ),
        width="grow",
        height="grow",
    )


class HomeView(rx.Widget):
    def build(self) -> rx.Widget:
        return rx.Column(
            rx.Stack(
                # Slideshow
                rx.Column(
                    rx.Slideshow(
                        rx.Rectangle(
                            child=rx.Text(
                                "Beautiful\nby Default",
                                margin_top=5,
                                margin_bottom=5,
                                align_x=0.3,
                                align_y=0.1,
                                style=rx.TextStyle(
                                    font_color=rx.Color.BLACK,
                                    font_size=7,
                                    font_weight="bold",
                                ),
                            ),
                            style=rx.BoxStyle(
                                fill=rx.ImageFill(
                                    Path().resolve()
                                    / "website"
                                    / "assets"
                                    / "material-backgrounds"
                                    / "pawel-czerwinski-ruJm3dBXCqw-unsplash.jpg",
                                    fill_mode="zoom",
                                ),
                            ),
                            width="grow",
                            height="grow",
                        ),
                        make_slideshow_placeholder(0),
                        # make_slideshow_placeholder(1),
                        # make_slideshow_placeholder(2),
                        # make_slideshow_placeholder(3),
                        width="grow",
                        linger_time=3,
                        height=45,
                    ),
                    rx.Rectangle(
                        style=rx.BoxStyle(fill=theme.THEME.surface_color),
                        height=11,
                    ),
                ),
                # Testimonials
                comps.Testimonials(
                    align_y=1,
                ),
            ),
            # Features
            comps.HoverCard(0),
            comps.HoverCard(1),
            comps.HoverCard(0),
            comps.HoverCard(1),
            # TODO: Point to how to get started
            # ...
        )
