import reflex as rx

from .. import theme


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
            align_y=0.5,
            on_press=lambda _: self.session.navigate_to("/" + self.route),
        )


class NavigationBar(rx.Widget):
    active_route: str
    is_wide: bool = False

    def build(self) -> rx.Widget:
        surface_color = theme.THEME.surface_color
        text_color = theme.THEME.text_color_for(surface_color)

        # If the page is narrow, fill most of the width with the navigation bar.
        # Otherwise fall back to a fixed width.
        width_trip = theme.CENTER_COLUMN_WIDTH + 25

        if self.is_wide:
            bar_width = theme.CENTER_COLUMN_WIDTH + 20
            bar_align_x = 0.5
        else:
            bar_width = "grow"
            bar_align_x = None

        # bar_align_x = None
        print(bar_width, bar_align_x)

        return rx.SizeTripSwitch(
            rx.Rectangle(
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
                        spacing=4.0,
                        margin_right=4.0,
                        align_x=1.0,
                        width="grow",
                    ),
                    width="grow",
                ),
                style=rx.BoxStyle(
                    fill=surface_color,
                    corner_radius=(
                        0,
                        0,
                        theme.LARGE_CORNER_RADIUS,
                        theme.LARGE_CORNER_RADIUS,
                    ),
                    shadow_color=theme.THEME.shadow_color,
                    shadow_radius=theme.THEME.shadow_radius,
                ),
                width=bar_width,
                align_x=bar_align_x,
                margin_x=2.0,
            ),
            width="grow",
            width_threshold=width_trip,
            is_wide=NavigationBar.is_wide,
        )


class NavigationBarDeadSpace(rx.Widget):
    def build(self) -> rx.Widget:
        return rx.Rectangle(
            style=rx.BoxStyle(
                fill=theme.THEME.background_color,
                # fill=theme.THEME.surface_color,
            ),
            height=8,
            width="grow",
        )
