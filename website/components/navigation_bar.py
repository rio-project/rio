import random

import reflex as rx

from .. import common, theme

# Random images to choose from for the spacer background
IMAGES = (
    common.ASSETS_DIR
    / "material-backgrounds"
    / "pawel-czerwinski-ruJm3dBXCqw-unsplash.jpg",
)


class NavigationButton(rx.Widget):
    text: str
    route: str
    active_route: str

    def build(self) -> rx.Widget:
        if self.route == self.active_route:
            color = theme.THEME.primary_color.replace(opacity=0.3)
        else:
            color = rx.Color.TRANSPARENT

        return rx.Button(
            self.text,
            color=color,
            width=5,
            align_y=0.5,
            on_press=lambda _: self.session.navigate_to("/" + self.route),
        )


class NavigationBar(rx.Widget):
    active_route: str

    def on_route_change(self) -> None:
        try:
            self.active_route = self.session.current_route[0]
        except IndexError:
            self.active_route = ""

    def build(self) -> rx.Widget:
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

        return rx.Rectangle(
            child=rx.Row(
                rx.Row(
                    rx.Icon(
                        "star",
                        width=3.0,
                        height=3.0,
                        margin_left=2,
                        fill=theme.THEME.primary_color,
                    ),
                    rx.Text(
                        "reflex",
                        style=rx.TextStyle(
                            font_size=1.5,
                            font_weight="bold",
                            font_color=text_color,
                        ),
                    ),
                    spacing=0.7,
                ),
                rx.Spacer(),
                rx.Row(
                    NavigationButton(
                        "Home",
                        "",
                        self.active_route,
                    ),
                    NavigationButton(
                        "News",
                        "posts",
                        self.active_route,
                    ),
                    NavigationButton(
                        "Docs",
                        "documentation",
                        self.active_route,
                    ),
                    NavigationButton(
                        "Tools",
                        "tools",
                        self.active_route,
                    ),
                    NavigationButton(
                        "About Us",
                        "about",
                        self.active_route,
                    ),
                    spacing=1.5,
                    margin_right=4.0,
                ),
            ),
            style=rx.BoxStyle(
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


class NavigationBarDeadSpace(rx.Widget):
    """
    The Navigation Bar hovers above other content, necessitating a spacer to
    prevent real content from being obscured.

    This widget is that spacer. it fills itself with a random background image
    to provide visual interest.
    """

    height: float = 8

    def build(self) -> rx.Widget:
        return rx.Rectangle(
            style=rx.BoxStyle(
                fill=rx.ImageFill(
                    random.choice(IMAGES),
                    fill_mode="zoom",
                ),
            ),
            height=self.height,
            width="grow",
        )
