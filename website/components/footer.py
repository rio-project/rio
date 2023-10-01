from typing import *  # type: ignore

import rio

from .. import theme


class FooterColumn(rio.Widget):
    entries: List[Tuple[str, Union[str, rio.URL]]]

    def build(self) -> rio.Widget:
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


class Footer(rio.Widget):
    def build(self) -> rio.Widget:
        return rio.Rectangle(
            child=rio.Column(
                rio.Text(
                    "Made with ❤️ in Vienna",
                    style=rio.TextStyle(
                        fill=rio.Color.WHITE,
                    ),
                    margin_bottom=2,
                ),
                rio.Row(
                    FooterColumn(
                        entries=[
                            ("About", "#"),
                            ("Blog", "#"),
                            ("Contact", "#"),
                        ],
                    ),
                    FooterColumn(
                        entries=[
                            ("Twitter", "#"),
                            ("LinkedIn", "#"),
                            ("GitHub", "#"),
                        ],
                    ),
                    FooterColumn(
                        entries=[
                            ("Privacy", rio.URL("http://google.com")),
                            ("Terms", "ddg.gg"),
                            ("Docs", "/documentation"),
                        ],
                    ),
                    spacing=6.0,
                    align_x=0.5,
                ),
                margin=2,
            ),
            style=rio.BoxStyle(
                fill=theme.THEME.surface_color.darker(0.4),
            ),
        )
