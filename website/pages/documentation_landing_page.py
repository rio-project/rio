from typing import *  # type: ignore

import rio

from .. import theme


class ButtonCard(rio.Component):
    title: str
    details: str
    target_url: rio.URL

    def build(self) -> rio.Component:
        return rio.Card(
            content=rio.Row(
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
                    width=20,
                    spacing=1,
                ),
                rio.Spacer(),
                rio.Icon(
                    "material/arrow-forward",
                    height=2,
                    width=2,
                    align_x=1,
                    align_y=0,
                ),
                spacing=2,
                margin=2,
            ),
            corner_radius=theme.THEME.corner_radius_large,
            on_press=lambda: self.session.navigate_to(self.target_url),
        )


class LargeNavigationButtons(rio.Component):
    def build(self) -> rio.Component:
        return rio.Row(
            rio.Column(
                ButtonCard(
                    "Getting Started",
                    "New to Rio? Start here.",
                    rio.URL("/documentation/tutorial-biography/1-rio-setup"),
                ),
                ButtonCard(
                    "How-To Guides",
                    "See how to add pages, navigation and accomplish other common tasks with Rio.",
                    rio.URL("/documentation/how-to"),
                ),
                ButtonCard(
                    "API Reference",
                    "Detailed API documentation for everything Rio.",
                    rio.URL("/documentation/component/button"),
                ),
                ButtonCard(
                    "Examples",
                    "See Rio in action with these examples.",
                    rio.URL("/documentation/todo"),
                ),
                spacing=2,
            ),
            rio.Image(
                theme.get_random_material_image(),
                width="grow",
                height="grow",
                corner_radius=theme.THEME.corner_radius_large,
                fill_mode="zoom",
            ),
            spacing=2,
        )


class DocumentationLandingPage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.MarkdownView(
                """
# Welcome to the Rio Documentation

Rio is your friendly companion for web and app development, especially if you're
not a web design expert but know some Python.

This page is a perfect starting point to explore Rio and learn how to build your
very own web apps. Whether you're a beginner or have specific questions, Rio is
here to simplify things for you.
""",
                margin_bottom=2,
            ),
            LargeNavigationButtons(),
            rio.Spacer(),
            width=90,  # TODO
            align_x=0.5,
        )
