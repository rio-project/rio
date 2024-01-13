from dataclasses import field
from typing import *  # type: ignore

import rio


class Subpage(rio.Component):
    child: rio.Component
    even: bool
    fill: Optional[rio.FillLike] = None

    def build(self) -> rio.Component:
        if self.fill is None:
            fill = (
                self.session.theme.neutral_color
                if self.even
                else self.session.theme.background_color
            )
            # fill = rio.LinearGradientFill(
            #     (self.session.theme.background_color, 0),
            #     (self.session.theme.neutral_color, 1),
            #     angle_degrees=270,
            # )
        else:
            fill = self.fill

        return rio.Card(
            child=rio.Container(
                self.child,
                align_x=0.5,
                align_y=0.5,
            ),
            # style=rio.BoxStyle(
            #     fill=fill,
            # ),
            color="neutral" if self.even else "background",
            corner_radius=0,
            height=60,
        )
