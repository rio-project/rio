from __future__ import annotations

import copy
from dataclasses import KW_ONLY, field
from typing import *  # type: ignore

from uniserde import Jsonable, JsonDoc

import reflex as rx

from .. import app_server, theme
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
    style: Optional[rx.BoxStyle] = None

    def _custom_serialize(self, server: app_server.AppServer) -> JsonDoc:
        # Determine a style
        if self.style is None:
            thm = self.session.attachments[rx.Theme]
            box_style = rx.BoxStyle(
                fill=thm.surface_color_variant,
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
            "boxStyle": box_style._serialize(server),
        }


Plot._unique_id = "Plot-builtin"
