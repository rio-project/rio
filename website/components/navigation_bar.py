import random

import rio

from .. import theme


class NavigationBar(rio.Component):
    @rio.event.on_page_change
    async def _on_page_change(self) -> None:
        await self.force_refresh()

    def _on_navigation_button_press(self, ev: rio.SwitcherBarChangeEvent[str]) -> None:
        self.session.navigate_to(f"/{ev.value}")

    def build(self) -> rio.Component:
        surface_color = theme.THEME.neutral_palette.background
        text_color = theme.THEME.text_color_for(surface_color)

        # If the page is narrow, fill most of the width with the navigation bar.
        # Otherwise fall back to a fixed width.
        if self.session.window_width > 110:
            bar_width = 106  # width - 2 * margin
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
                rio.Icon(
                    "rio/logo:color",
                    width=2.7,
                    height=2.7,
                    margin_left=2.5,
                ),
                rio.Text(
                    "Rio",
                    style=rio.TextStyle(
                        font_size=1.5,
                        font_weight="bold",
                        fill=text_color,
                    ),
                    margin_left=0.3,
                ),
                rio.Spacer(),
                rio.SwitcherBar(
                    names=[
                        "Home",
                        "Docs",
                        "About Us",
                    ],
                    values=[
                        "",
                        "documentation",
                        "about-us",
                    ],
                    selected_value=active_url_fragment,
                    color="primary",
                    spacing=1,
                    on_change=self._on_navigation_button_press,
                    margin_right=0.5,
                    align_y=0.5,
                ),
                rio.Tooltip(
                    rio.Link(
                        rio.IconButton(
                            "thirdparty/github-logo",
                            color="primary",
                            style="plain",
                            size=2.2,
                        ),
                        target_url="https://github.com/rio-project/rio",
                        open_in_new_tab=True,
                    ),
                    "Github",
                    position="bottom",
                    margin_right=1.0,
                ),
                rio.Link(
                    rio.Tooltip(
                        rio.IconButton(
                            "thirdparty/discord-logo",
                            color="primary",
                            style="plain",
                            size=2.2,
                        ),
                        "Discord",
                        position="bottom",
                        margin_right=2.0,
                    ),
                    target_url="https://discord.com/todo",
                    open_in_new_tab=True,
                ),
            ),
            style=rio.BoxStyle(
                fill=surface_color,
                corner_radius=(theme.THEME.corner_radius_large),
                shadow_color=theme.THEME.shadow_color,
                shadow_radius=0.4,
                shadow_offset_y=0.1,
            ),
            margin_x=2.0,
            width=bar_width,
            align_x=bar_align_x,
        )
