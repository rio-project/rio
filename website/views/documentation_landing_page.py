from typing import *  # type: ignore

import rio

from .. import theme


class ButtonCard(rio.Widget):
    title: str
    details: str
    target_url: rio.URL

    def build(self) -> rio.Widget:
        return rio.Card(
            child=rio.Row(
                rio.Column(
                    rio.Text(
                        self.title,
                        style="heading2",
                        align_x=0,
                    ),
                    rio.Text(
                        self.details,
                        align_x=0,
                        multiline=True,
                    ),
                    spacing=1,
                ),
                rio.Spacer(),
                rio.Icon(
                    "material/arrow-forward",
                    height=2,
                    width=2,
                    align_x=1,
                ),
                spacing=2,
                margin=2,
            ),
            corner_radius=theme.THEME.corner_radius_large,
            on_press=lambda: self.session.navigate_to(self.target_url),
        )


class LargeNavigationButtons(rio.Widget):
    def build(self) -> rio.Widget:
        return rio.Row(
            rio.Column(
                ButtonCard(
                    "Getting Started",
                    "New to Rio? Start here.",
                    rio.URL("/documentation/first-steps"),
                ),
                ButtonCard(
                    "How-To Guides",
                    "See how to add pages, navigation and accomplish other common tasks with Rio.",
                    rio.URL("/documentation/how-to"),
                ),
                ButtonCard(
                    "API Reference",
                    "Detailed API documentation for all of Rio.",
                    rio.URL("/documentation/api-reference"),
                ),
                spacing=1,
            ),
            rio.Image(
                theme.get_random_material_image(),
                width="grow",
                height="grow",
                corner_radius=theme.THEME.corner_radius_large,
                fill_mode="zoom",
            ),
            spacing=1,
        )


class DocumentationLandingPage(rio.Widget):
    def build(self) -> rio.Widget:
        return rio.Column(
            # rio.Text(
            #     "Welcome to the Rio Documentation",
            #     style="heading1",
            #     margin_bottom=5,
            # ),
            LargeNavigationButtons(),
            rio.Spacer(),
            width=theme.CENTER_COLUMN_WIDTH,
            align_x=0.5,
        )
