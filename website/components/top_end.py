import random
from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from .. import components as comps
from .. import theme


class TopEnd(rio.Component):
    """
    The Navigation Bar hovers above other content, necessitating a spacer to
    prevent real content from being obscured. This component is that spacer.
    """

    height: float = 8

    def build(self) -> rio.Component:
        return rio.Rectangle(
            style=rio.BoxStyle(
                fill=rio.ImageFill(
                    random.choice(theme.GENERIC_MATERIAL_IMAGES),
                    fill_mode="zoom",
                ),
            ),
            height=self.height,
            width="grow",
            margin_bottom=3,
        )
