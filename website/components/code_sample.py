from typing import *  # type: ignore

import rio

from .. import components as comps
from .. import theme


class CodeSample(rio.Component):
    title: str
    text: str
    source_code: str
    build_result: rio.Component
    line_indices_to_component_keys: List[Optional[str]]

    def build(self) -> rio.Component:
        return rio.Column(
            rio.Container(
                rio.Text(
                    self.title,
                    multiline=True,
                    style=theme.ACTION_TITLE_STYLE,
                ),
                # width=theme.COLUMN_WIDTH,
                margin_top=4,
                # align_x=0.5,
            ),
            rio.Column(
                rio.CodeExplorer(
                    self.source_code,
                    self.build_result,
                    self.line_indices_to_component_keys,
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
                spacing=5,
                height="grow",
                align_y=0.5,
            ),
            height=theme.get_subpage_height(self.session),
        )
