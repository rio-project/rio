from typing import *  # type: ignore

import rio

from .. import components as comps
from .. import theme


class ShadedSubpage(rio.Component):
    child: rio.Component

    def build(self) -> rio.Component:
        return rio.Card(
            self.child,
            corner_radius=0,
        )
