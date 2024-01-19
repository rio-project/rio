from typing import *  # type: ignore

import rio

from .. import theme


class FooterColumn(rio.Component):
    entries: list[tuple[str, Union[str, rio.URL]]]

    def build(self) -> rio.Component:
        return rio.Column(
            *[
                rio.Link(
                    child=entry[0],
                    target_url=entry[1],
                )
                for entry in self.entries
            ],
            spacing=1.0,
        )


class Footer(rio.Component):
    def build(self) -> rio.Component:
        return rio.Rectangle(
            child=rio.Column(
                # rio.Rectangle(
                #     style=rio.BoxStyle(
                #         fill=theme.THEME.background_palette.background,
                #         corner_radius=(
                #             0,
                #             0,
                #             theme.THEME.corner_radius_large,
                #             theme.THEME.corner_radius_large,
                #         ),
                #     ),
                #     height=theme.THEME.corner_radius_large,
                # ),
                rio.Text(
                    "Made with ❤️ in Vienna",
                    style=rio.TextStyle(
                        fill=theme.THEME.background_palette.background,
                        font_size=1.1,
                    ),
                    margin_top=3,
                    margin_bottom=0.6,
                ),
                rio.Text(
                    "by the Rio Team & Contributors",
                    style=rio.TextStyle(
                        fill=rio.Color.WHITE,
                    ),
                    margin_bottom=3,
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
                    spacing=6.0,
                    align_x=0.5,
                ),
                margin=0,
                margin_bottom=5,
            ),
            style=rio.BoxStyle(
                fill=self.session.theme.hud_color,
            ),
        )
