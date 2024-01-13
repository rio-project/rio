import rio

from .. import components as comps
from .. import theme


class CodeSample(rio.Component):
    title: str
    text: str
    code: str

    def build(self) -> rio.Component:
        return rio.Column(
            rio.Container(
                rio.Text(
                    self.title,
                    multiline=True,
                    style=rio.TextStyle(
                        font_size=theme.TITLE_HEIGHT,
                    ),
                ),
                width=theme.COLUMN_WIDTH,
                align_x=0.5,
            ),
            rio.Container(
                rio.Text(
                    self.text,
                    multiline=True,
                    align_x=0.5,
                    style=rio.TextStyle(
                        font_size=theme.ACTION_TEXT_HEIGHT,
                    ),
                ),
                width=theme.COLUMN_WIDTH,
                align_x=0.5,
            ),
            comps.CodeExplorer(self.code),
            spacing=2,
        )
