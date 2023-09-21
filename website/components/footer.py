from typing import *  # type: ignore

import rio as rx

from .. import theme


class FooterColumn(rx.Widget):
    entries: List[Tuple[str, Union[str, rx.URL]]]

    def build(self) -> rx.Widget:
        text_style = rx.TextStyle(
            font_color=theme.THEME.text_color_on_dark,
        )

        return rx.Column(
            *[
                rx.Link(
                    child=entry[0],
                    link=entry[1],
                    # style=text_style,
                )
                for entry in self.entries
            ],
            spacing=1.0,
        )


class Footer(rx.Widget):
    def build(self) -> rx.Widget:
        return rx.Rectangle(
            child=rx.Column(
                rx.Text(
                    "Made with ❤️ in Vienna",
                    style=rx.TextStyle(
                        font_color=rx.Color.WHITE,
                    ),
                    margin_bottom=2,
                ),
                rx.Row(
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
                            ("Privacy", rx.URL("http://google.com")),
                            ("Terms", "ddg.gg"),
                            ("Docs", "/documentation"),
                        ],
                    ),
                    spacing=6.0,
                    align_x=0.5,
                ),
                margin=2,
            ),
            style=rx.BoxStyle(
                fill=theme.THEME.surface_color.darker(0.4),
            ),
        )
