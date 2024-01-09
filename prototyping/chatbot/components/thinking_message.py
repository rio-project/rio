from dataclasses import dataclass
from typing import *  # type: ignore

import rio


class ThinkingMessage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Card(
            rio.Row(
                rio.Column(
                    rio.Row(
                        rio.Icon(
                            "castle",
                            fill="secondary",
                        ),
                        rio.Text(
                            "Hyper Dyper Ultra Bot",
                            style=rio.TextStyle(
                                fill=self.session.theme.secondary_color,
                            ),
                        ),
                        spacing=1,
                        align_x=0,
                    ),
                    rio.Text(
                        "Thinking...",
                        style="dim",
                        align_x=0,
                    ),
                    spacing=1.0,
                ),
                rio.Spacer(),
                rio.ProgressCircle(progress=None, size=2.0),
                spacing=1.5,
            ),
            # width=30,
            # align_x=0,
            margin_right=10,
        )
