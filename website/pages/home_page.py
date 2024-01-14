from pathlib import Path
from typing import *  # type: ignore

import rio

from .. import components as comps
from .. import theme


class HomePage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            comps.Hero(),
            comps.ShadedSubpage(
                comps.CodeSample(
                    "Create your own components",
                    "React lets you build user interfaces out of individual pieces called components. Create your own React components like Thumbnail, LikeButton, and Video. Then combine them into entire screens, pages, and apps.",
                    """
class StupidComponent(rio.Component):
    code: str

    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text("Line 1"),
            rio.Text("Line 2"),
            rio.Spacer(),
        )
""".strip(),
                    rio.Column(
                        rio.Text("Line 1", key="text1"),
                        rio.Text("Line 2", key="text2"),
                        rio.Spacer(key="spacer1"),
                        key="column1",
                        width=20,
                    ),
                    line_indices_to_component_keys=[
                        None,
                        None,
                        None,
                        None,
                        "column1",
                        "text1",
                        "text2",
                        "spacer1",
                        "column1",
                    ],
                ),
            ),
            comps.CodeSample(
                "Create your own components",
                "React lets you build user interfaces out of individual pieces called components. Create your own React components like Thumbnail, LikeButton, and Video. Then combine them into entire screens, pages, and apps.",
                """
class WhatIsThisComponent(rio.Component):
    code: str

    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text("Line 1"),
            rio.Text("Line 2"),
            rio.Spacer(),
        )
""".strip(),
                rio.Column(
                    rio.Text("Line 1", key="text1"),
                    rio.Text("Line 2", key="text2"),
                    rio.Spacer(key="spacer1"),
                    key="column1",
                    width=20,
                ),
                line_indices_to_component_keys=[
                    None,
                    None,
                    None,
                    None,
                    "column1",
                    "text1",
                    "text2",
                    "spacer1",
                    "column1",
                ],
            ),
            comps.GettingStarted(),
            comps.ComponentShowcase(),
            comps.Community(),
        )
