import random
from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from .. import components as comps
from .. import theme


class BottomEnd(rio.Component):
    """
    Provides a smooth transition from the page content to the footer.
    """

    def build(self) -> rio.Component:
        return rio.Row(
            rio.Icon(
                "styling/rounded-corner-bottom-left",
                fill=self.session.theme.hud_color,
                width=4,
                height=4,
                align_x=0,
            ),
            rio.Spacer(),
            rio.Icon(
                "styling/rounded-corner-bottom-right",
                fill=self.session.theme.hud_color,
                width=4,
                height=4,
                align_x=0,
            ),
            width="grow",
        )
