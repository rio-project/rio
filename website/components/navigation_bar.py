import random
from dataclasses import field

import rio

from .. import common, theme

# Random images to choose from for the spacer background
IMAGES = (
    common.ASSETS_DIR
    / "material-backgrounds"
    / "pawel-czerwinski-ruJm3dBXCqw-unsplash.jpg",
)


class NavigationButton(rio.Widget):
    text: str
    route: str
    is_active: bool = False

    def on_create(self) -> None:
        self.on_route_change()

    def on_route_change(self) -> None:
        try:
            self.is_active = self.session.active_route.parts[1] == self.route
        except IndexError:
            self.is_active = False

    def build(self) -> rio.Widget:
        if self.is_active:
            color = theme.THEME.primary_color.replace(opacity=0.3)
        else:
            color = rio.Color.TRANSPARENT

        return rio.Button(
            self.text,
            color=color,
            width=5,
            align_y=0.5,
            on_press=lambda _: self.session.navigate_to("/" + self.route),
        )


class NavigationBar(rio.Widget):
    def build(self) -> rio.Widget:
        surface_color = theme.THEME.surface_color
        text_color = theme.THEME.text_color_for(surface_color)

        # If the page is narrow, fill most of the width with the navigation bar.
        # Otherwise fall back to a fixed width.
        width_trip = theme.CENTER_COLUMN_WIDTH + 25

        if self.session.window_width > width_trip:
            bar_width = theme.CENTER_COLUMN_WIDTH + 20
            bar_align_x = 0.5
        else:
            bar_width = "grow"
            bar_align_x = None

        return rio.Rectangle(
            child=rio.Row(
                rio.Row(
                    rio.Icon(
                        "star",
                        width=3.0,
                        height=3.0,
                        margin_left=2,
                        fill=theme.THEME.primary_color,
                    ),
                    rio.Text(
                        "rio",
                        style=rio.TextStyle(
                            font_size=1.5,
                            font_weight="bold",
                            font_color=text_color,
                        ),
                    ),
                    spacing=0.7,
                ),
                rio.Spacer(),
                rio.Row(
                    NavigationButton(
                        "Home",
                        "",
                    ),
                    NavigationButton(
                        "News",
                        "posts",
                    ),
                    NavigationButton(
                        "Docs",
                        "documentation",
                    ),
                    NavigationButton(
                        "Tools",
                        "tools",
                    ),
                    NavigationButton(
                        "About Us",
                        "about",
                    ),
                    spacing=1.5,
                    margin_right=4.0,
                ),
            ),
            style=rio.BoxStyle(
                fill=surface_color,
                corner_radius=(
                    0,
                    0,
                    theme.THEME.corner_radius_large,
                    theme.THEME.corner_radius_large,
                ),
                shadow_color=theme.THEME.shadow_color,
                shadow_radius=theme.THEME.shadow_radius,
            ),
            width=bar_width,
            align_x=bar_align_x,
            margin_x=2.0,
        )


class NavigationBarDeadSpace(rio.Widget):
    """
    The Navigation Bar hovers above other content, necessitating a spacer to
    prevent real content from being obscured.

    This widget is that spacer. it fills itself with a random background image
    to provide visual interest.
    """

    height: float = 8

    def build(self) -> rio.Widget:
        return rio.Rectangle(
            style=rio.BoxStyle(
                fill=rio.ImageFill(
                    random.choice(IMAGES),
                    fill_mode="zoom",
                ),
            ),
            height=self.height,
            width="grow",
        )
