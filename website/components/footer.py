from typing import *  # type: ignore

import rio

from .. import theme


class FooterColumn(rio.Component):
    entries: List[Tuple[str, Union[str, rio.URL]]]

    def build(self) -> rio.Component:
        text_style = rio.TextStyle(
            fill=theme.THEME.text_color_on_dark,
        )

        return rio.Column(
            *[
                rio.Link(
                    child=entry[0],
                    target_url=entry[1],
                    # style=text_style,
                )
                for entry in self.entries
            ],
            spacing=1.0,
        )


class Footer(rio.Component):
    def build(self) -> rio.Component:
        return rio.Rectangle(
            child=rio.Column(
                rio.Rectangle(
                    style=rio.BoxStyle(
                        fill=rio.Color.WHITE,
                        corner_radius=(
                            0,
                            0,
                            theme.THEME.corner_radius_large,
                            theme.THEME.corner_radius_large,
                        ),
                    ),
                    height=theme.THEME.corner_radius_large,
                ),
                rio.Text(
                    "Made with ❤️ in Vienna",
                    style=rio.TextStyle(
                        fill=theme.THEME.background_color,
                        font_size=1.1,
                    ),
                    margin_top=4,
                    margin_bottom=0.6,
                ),
                rio.Text(
                    "by the Rio Team & Contributors",
                    style=rio.TextStyle(
                        fill=rio.Color.WHITE,
                    ),
                    margin_bottom=4,
                ),
                rio.Row(
                    FooterColumn(
                        entries=[
                            ("About", "#"),
                            ("Blog", "#"),
                            ("Contact", "#"),
                        ],  # type: ignore
                    ),
                    FooterColumn(
                        entries=[
                            ("Twitter", "#"),
                            ("LinkedIn", "#"),
                            ("GitHub", "https://github.com/rio-project/rio"),
                        ],  # type: ignore
                    ),
                    FooterColumn(
                        entries=[
                            ("Privacy", rio.URL("http://google.com")),
                            ("Terms", "ddg.gg"),
                            ("Docs", "/documentation"),
                        ],  # type: ignore
                    ),
                    spacing=8.0,
                    align_x=0.5,
                ),
                margin=0,
                margin_bottom=7,
            ),
            style=rio.BoxStyle(
                fill=theme.THEME.surface_color.darker(0.8),
            ),
        )
