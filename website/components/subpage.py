from dataclasses import field
from typing import *  # type: ignore

import rio

from .. import theme


class Subpage(rio.Component):
    child: rio.Component
    color: rio.ColorSet

    def build(self) -> rio.Component:
        return rio.Card(
            child=rio.Container(
                self.child,
                align_x=0.5,
                align_y=0.5,
            ),
            color=self.color,
            corner_radius=0,
            height=theme.SUBPAGE_HEIGHT,
        )
