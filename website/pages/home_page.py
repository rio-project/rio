from pathlib import Path
from typing import *  # type: ignore

import rio

from .. import components as comps
from .. import theme


class HomePage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            comps.Hero(
                height=theme.SUBPAGE_HEIGHT,
            ),
            comps.Subpage(
                comps.CodeSample(
                    "Create your own components",
                    "React lets you build user interfaces out of individual pieces called components. Create your own React components like Thumbnail, LikeButton, and Video. Then combine them into entire screens, pages, and apps.",
                    """
class CodeExplorer(rio.Component):
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
                        height=16,
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
                color="neutral",
            ),
            comps.Subpage(
                comps.CodeSample(
                    "Create your own components",
                    "React lets you build user interfaces out of individual pieces called components. Create your own React components like Thumbnail, LikeButton, and Video. Then combine them into entire screens, pages, and apps.",
                    """
class CodeExplorer(rio.Component):
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
                        height=16,
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
                color="background",
            ),
            comps.GettingStarted(
                height=theme.SUBPAGE_HEIGHT,
            ),
            comps.Subpage(
                comps.ComponentShowcase(),
                color="neutral",
            ),
            comps.Subpage(
                comps.Community(),
                color="background",
            ),
        )
