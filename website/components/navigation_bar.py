import random
from pathlib import Path

import rio

from .. import theme


class NavigationBar(rio.Component):
    def _on_navigation_button_press(self, ev: rio.SwitcherBarChangeEvent[str]) -> None:
        self.session.navigate_to("/" + ev.value)

    def build(self) -> rio.Component:
        surface_color = theme.THEME.neutral_palette.background
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

        # Which navigation button is active?
        try:
            active_url_fragment = self.session.active_page_url.parts[1]
        except IndexError:
            active_url_fragment = ""

        return rio.Rectangle(
            child=rio.Row(
                rio.Row(
                    rio.Image(
                        Path("website/assets/rio-logo.png"),
                        width=1.7,
                        height=1.7,
                        margin_left=2.5,
                    ),
                    rio.Text(
                        "rio",
                        style=rio.TextStyle(
                            font_size=1.5,
                            font_weight="bold",
                            fill=text_color,
                        ),
                    ),
                    spacing=0.8,
                ),
                rio.Spacer(),
                rio.SwitcherBar(
                    {
                        "Home": "",
                        "Docs": "documentation",
                        "Tools": "tools",
                        "About Us": "about",
                    },
                    selected_value=active_url_fragment,
                    color="primary",
                    on_change=self._on_navigation_button_press,
                    margin_right=4.0,
                    align_y=0.5,
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

    This component is that spacer. it fills itself with a random background image
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
