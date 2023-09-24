from typing import *  # type: ignore

import rio

from .. import theme


class FlatCard(rio.Widget):
    child: rio.Widget
    corner_radius: Union[
        float, Tuple[float, float, float, float]
    ] = theme.THEME.corner_radius_large

    def build(self) -> rio.Widget:
        return rio.Card(
            rio.Container(
                self.child,
                margin=2,
            ),
            corner_radius=self.corner_radius,
            hover_height=0,
            elevate_on_hover=0,
        )
