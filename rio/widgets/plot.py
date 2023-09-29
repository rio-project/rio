from __future__ import annotations

import copy
from dataclasses import KW_ONLY
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import widget_base

try:
    import plotly  # type: ignore
    import plotly.graph_objects  # type: ignore
except ImportError:
    if TYPE_CHECKING:
        import plotly  # type: ignore


__all__ = [
    "Plot",
]


class Plot(widget_base.FundamentalWidget):
    """
    Displays the given figure in the website.

    The `style` argument can be used to customize the appearance of the plot.
    The following attributes are supported:

    - `fill`
    - `corner_radius`
    """

    figure: plotly.graph_objects.Figure
    _: KW_ONLY
    style: Optional[rio.BoxStyle] = None

    def _custom_serialize(self) -> JsonDoc:
        # Determine a style
        if self.style is None:
            thm = self.session.attachments[rio.Theme]
            box_style = rio.BoxStyle(
                fill=thm.surface_color_variant,
                corner_radius=thm.corner_radius_small,
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
            "boxStyle": box_style._serialize(self.session),
        }


Plot._unique_id = "Plot-builtin"