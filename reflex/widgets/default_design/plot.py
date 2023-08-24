from __future__ import annotations

import copy
from dataclasses import KW_ONLY, field
from typing import *  # type: ignore

from uniserde import JsonDoc

import reflex as rx

from .. import fundamental
from . import theme

try:
    import plotly
    import plotly.graph_objects
except ImportError:
    if TYPE_CHECKING:
        import plotly


__all__ = [
    "Plot",
]


class Plot(fundamental.HtmlWidget):
    """
    Displays the given figure in the website.

    The `style` argument can be used to customize the appearance of the plot.
    The following attributes are supported:

    - `fill`
    - `corner_radius`
    """

    figure: plotly.graph_objects.Figure
    _: KW_ONLY
    style: Optional[fundamental.BoxStyle] = None

    def _custom_serialize(self) -> JsonDoc:
        # Determine a style
        if self.style is None:
            thm = self.session.attachments[theme.Theme]
            box_style = fundamental.BoxStyle(
                fill=thm.neutral_contrast_color,
                corner_radius=thm.corner_radius,
            )
        else:
            box_style = self.style

        # Make the plot transparent, so the background configured by JavaScript
        # shines through.
        figure = copy.copy(self.figure)
        figure.update_layout(
            {
                "plot_bgcolor": "rgba(0,0,0,0)",
                "paper_bgcolor": "rgba(0,0,0,0)",
            }
        )

        return {
            "plotJson": figure.to_json(),
            "boxStyle": box_style._serialize(),
        }


Plot._unique_id = "Plot-builtin"
