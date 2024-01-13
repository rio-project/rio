import rio

from .. import theme


class Hero(rio.Component):
    def build(self) -> rio.Component:
        logo_height = 42
        aspect = 1282.2842 / 1154.8138

        return rio.Row(
            rio.Column(
                rio.Row(
                    rio.Icon(
                        "rio/logo:color",
                        width=8,
                        height=8,
                    ),
                    rio.Text(
                        "Rio",
                        style=rio.TextStyle(
                            font_size=theme.TITLE_HEIGHT,
                            font_weight="bold",
                        ),
                    ),
                    margin_bottom=1,
                    align_x=0.5,
                ),
                rio.Text(
                    "Blabla, we're the coolest. Super easy to use and deploys in seconds.",
                    style=rio.TextStyle(
                        font_size=theme.ACTION_TEXT_HEIGHT,
                    ),
                    multiline=True,
                    width=30,
                ),
                rio.Row(
                    rio.Button(
                        "Get Started",
                    ),
                    rio.Button(
                        "API Reference",
                        style="minor",
                    ),
                    spacing=2,
                    margin_top=2,
                    align_x=0.5,
                ),
                width="grow",
                align_y=0.5,
            ),
            rio.Icon(
                "self/hero-shape",
                width="grow",
                height="grow",
                fill=rio.LinearGradientFill(
                    (self.session.theme.primary_color, 0),
                    (self.session.theme.secondary_color, 1),
                    angle_degrees=90,
                ),
            ),
        )
