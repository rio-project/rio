from pathlib import Path
from typing import *  # type: ignore

import rio

from .. import components as comps
from .. import theme


def make_slideshow_placeholder(variant: int) -> rio.Widget:
    colors = [
        rio.Color.RED,
        rio.Color.GREEN,
        rio.Color.BLUE,
        rio.Color.YELLOW,
        rio.Color.PURPLE,
        rio.Color.MAGENTA,
    ]

    return rio.Rectangle(
        child=rio.Text(
            f"Slideshow Page {variant}",
        ),
        style=rio.BoxStyle(
            fill=colors[variant % len(colors)],
        ),
        width="grow",
        height="grow",
    )


def make_slide(
    sess: rio.Session,
    foreground: rio.Widget,
    background: rio.ImageLike,
) -> rio.Widget:
    return rio.Rectangle(
        child=rio.Container(
            child=foreground,
            width=theme.get_center_column_width(sess),
            align_x=0.5,
            margin_top=6,
            margin_bottom=5,
        ),
        style=rio.BoxStyle(
            fill=rio.ImageFill(
                background,
                fill_mode="zoom",
            ),
        ),
        width="grow",
        height="grow",
    )


class HomeView(rio.Widget):
    def build(self) -> rio.Widget:
        return rio.Column(
            # Slideshow
            rio.Slideshow(
                make_slide(
                    self.session,
                    rio.Text(
                        "Beautiful\nby Default",
                        align_y=0,
                        align_x=0,
                        style=rio.TextStyle(
                            fill=rio.Color.BLACK,
                            font_size=7,
                            font_weight="bold",
                        ),
                    ),
                    Path().resolve()
                    / "website"
                    / "assets"
                    / "material-backgrounds"
                    / "pawel-czerwinski-ruJm3dBXCqw-unsplash.jpg",
                ),
                make_slideshow_placeholder(0),
                make_slideshow_placeholder(1),
                # make_slideshow_placeholder(2),
                # make_slideshow_placeholder(3),
                corner_radius=theme.THEME.corner_radius_large,
                width="grow",
                linger_time=3,
                height=45,
                margin_x=1,
                margin_top=1,
            ),
            # Testimonials
            comps.Testimonials(
                margin_top=1,
                margin_bottom=1,
            ),
            # Features
            comps.HoverCard(0),
            comps.HoverCard(1),
            comps.HoverCard(0),
            comps.HoverCard(1),
            # TODO: Point to how to get started
            # ...
        )
