from __future__ import annotations

import copy
from dataclasses import KW_ONLY, field
from typing import *  # type: ignore

from uniserde import JsonDoc

from ... import styling, theme
from . import widget_base

try:
    import plotly
    import plotly.graph_objects
except ImportError:
    if TYPE_CHECKING:
        import plotly


__all__ = ("Plot",)


_DEFAULT_STYLE = styling.BoxStyle(
    fill=theme.COLOR_NEUTRAL,
    corner_radius=theme.CORNER_RADIUS,
)


class Plot(widget_base.HtmlWidget):
    """
    Displays the given figure in the website.

    The `style` argument can be used to customize the appearance of the plot.
    The following attributes are supported:

    - `fill`
    - `corner_radius`
    """

    figure: plotly.graph_objects.Figure
    _: KW_ONLY
    style: styling.BoxStyle = field(default_factory=lambda: _DEFAULT_STYLE)

    def _custom_serialize(self) -> JsonDoc:
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
            "boxStyle": self.style._serialize(),
        }


Plot._unique_id = "Plot-builtin"
