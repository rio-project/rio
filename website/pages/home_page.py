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
class Dataset(rio.Component):
    def build(self) -> rio.Component:
        return rio.Row(
            rio.Icon("cloud", width=3, height=3),
            rio.Column(
                rio.Text("Dataset 1", align_x=0),
                rio.Text("CSV", align_x=0, style="dim"),
                align_y=0,
            ),
            rio.Spacer(),
            rio.IconButton("download", style="plain", size=3),
            spacing=1,
            width=20,
            margin=1.5,
        )
""".strip(),
                    rio.Card(
                        rio.Row(
                            rio.Icon(
                                "cloud",
                                width=3,
                                height=3,
                                key="icon1",
                            ),
                            rio.Column(
                                rio.Text(
                                    "Dataset 1",
                                    align_x=0,
                                    key="text1",
                                ),
                                rio.Text(
                                    "CSV",
                                    align_x=0,
                                    style="dim",
                                    key="text2",
                                ),
                                align_y=0,
                                key="column1",
                            ),
                            rio.Spacer(
                                key="spacer1",
                            ),
                            rio.IconButton(
                                "download",
                                style="plain",
                                size=3,
                                key="iconbutton1",
                            ),
                            spacing=1,
                            width=20,
                            margin=1.5,
                            key="row1",
                        ),
                        color="background",
                        corner_radius=2,
                        key="card1",
                    ),
                    line_indices_to_component_keys=[
                        "card1",
                        "card1",
                        "row1",
                        "icon1",
                        "column1",
                        "text1",
                        "text2",
                        "column1",
                        "column1",
                        "spacer1",
                        "iconbutton1",
                        "row1",
                        "row1",
                        "row1",
                        "row1",
                        "card1",  # Makes the highlight span the full height
                        None,  # Just here to stfu the type checker
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
            comps.ShadedSubpage(
                comps.Community(),
            ),
        )
