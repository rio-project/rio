from pathlib import Path
from typing import *  # type: ignore

import rio

from .. import components as comps
from .. import theme


class HomePage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            comps.Hero(),
            comps.Subpage(
                comps.CodeSample(
                    "Create user interfaces from components",
                    "React lets you build user interfaces out of individual pieces called components. Create your own React components like Thumbnail, LikeButton, and Video. Then combine them into entire screens, pages, and apps.",
                    """
class CodeExplorer(rio.Component):
    code: str

    def build(self) -> rio.Component:
        return rio.Row(
            rio.MarkdownView(
{rio.escape_markdown_code(self.code)}
                align_y=0.5,
            ),
            rio.Spacer(),
            rio.Card(
                rio.Text("Placeholder"),
                width=40,
                height=20,
                align_y=0.5,
            ),
        )
""",
                ),
                even=True,
            ),
            comps.Subpage(
                comps.CodeSample(
                    "Create user interfaces from components",
                    "React lets you build user interfaces out of individual pieces called components. Create your own React components like Thumbnail, LikeButton, and Video. Then combine them into entire screens, pages, and apps.",
                    """
class CodeExplorer(rio.Component):
    code: str

    def build(self) -> rio.Component:
        return rio.Row(
            rio.MarkdownView(
{rio.escape_markdown_code(self.code)}
                align_y=0.5,
            ),
            rio.Spacer(),
            rio.Card(
                rio.Text("Placeholder"),
                width=40,
                height=20,
                align_y=0.5,
            ),
        )
""",
                ),
                even=False,
            ),
            comps.GettingStarted(),
            comps.Subpage(
                comps.ComponentShowcase(),
                even=True,
            ),
            comps.Subpage(
                comps.Community(),
                even=False,
            ),
        )
