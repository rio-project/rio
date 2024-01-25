from typing import *  # type: ignore

import rio

from .. import components as comps
from .. import theme


class ShadedSubpage(rio.Component):
    content: rio.Component

    def build(self) -> rio.Component:
        return rio.Card(
            self.content,
            corner_radius=0,
        )
