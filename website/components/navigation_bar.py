import random
from dataclasses import field

import rio

from .. import theme


class NavigationButton(rio.Component):
    text: str
    route: str
    is_active: bool = False

    @rio.event.on_create
    def on_create(self) -> None:
        self.on_route_change()

    @rio.event.on_route_change
    def on_route_change(self) -> None:
        try:
            self.is_active = self.session.active_route.parts[1] == self.route
        except IndexError:
            self.is_active = False

    def build(self) -> rio.Component:
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


class NavigationBar(rio.Component):
    def build(self) -> rio.Component:
        surface_color = theme.THEME.surface_color
        text_color = theme.THEME.text_color_for(surface_color)

        # If the page is narrow, fill most of the width with the navigation bar.
        # Otherwise fall back to a fixed width.
        center_column_width = theme.get_center_column_width(self.session)
        width_trip = center_column_width + 25

        if self.session.window_width > width_trip:
            bar_width = center_column_width + 20
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
                            fill=text_color,
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
                corner_radius=(theme.THEME.corner_radius_large),
                shadow_color=theme.THEME.shadow_color,
                shadow_radius=0.4,
                shadow_offset_y=0.1,
            ),
            width=bar_width,
            align_x=bar_align_x,
            margin_x=2.0,
        )


class NavigationBarDeadSpace(rio.Component):
    """
    The Navigation Bar hovers above other content, necessitating a spacer to
    prevent real content from being obscured.

    This widget is that spacer. it fills itself with a random background image
    to provide visual interest.
    """

    height: float = 8

    def build(self) -> rio.Component:
        return rio.Rectangle(
            style=rio.BoxStyle(
                fill=rio.ImageFill(
                    random.choice(theme.GENERIC_MATERIAL_IMAGES),
                    fill_mode="zoom",
                ),
            ),
            height=self.height,
            width="grow",
        )
