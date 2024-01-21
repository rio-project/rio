from typing import *  # type: ignore
from typing import Any  # type: ignore

import rio

from .. import components as comps


class DocumentationPage(rio.Component):
    def build(self) -> rio.Component:
        wide = self.session.window_width > 90

        return rio.Column(
            comps.TopEnd(),
            rio.Row(
                rio.Spacer(width=1 + 12),
                rio.Overlay(
                    comps.DocsOutliner(
                        width=12,
                        margin_left=1,
                        align_x=0,
                        align_y=0.5,
                    ),
                ),
                rio.Container(
                    rio.PageView(
                        width=65 if wide else "grow",
                        height="grow",
                        margin_x=2,
                        align_x=0.5 if wide else None,
                    ),
                    width="grow",
                ),
                height="grow",
            ),
            comps.BottomEnd(),
        )
