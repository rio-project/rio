from __future__ import annotations

import base64
import copy
import io
from dataclasses import KW_ONLY
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .. import maybes
from . import component_base

if TYPE_CHECKING:
    import matplotlib.figure  # type: ignore
    import plotly.graph_objects  # type: ignore


__all__ = ["Plot"]


class Plot(component_base.FundamentalComponent):
    """
    Displays a graph.


    Attributes:
        figure: The `plotly` figure to display.

        style: Controls the appearance of the plot. The following attributes are supported:
            - `fill`
            - `corner_radius`
    """

    figure: matplotlib.figure.Figure | plotly.graph_objects.Figure
    _: KW_ONLY
    style: Optional[rio.BoxStyle] = None

    def _custom_serialize(self) -> JsonDoc:
        # Determine a style
        if self.style is None:
            thm = self.session.theme
            box_style = rio.BoxStyle(
                fill=thm.neutral_palette.background_variant,
                corner_radius=thm.corner_radius_small,
            )
        else:
            box_style = self.style

        figure = self.figure
        plot: JsonDoc
        if isinstance(figure, maybes.PLOTLY_GRAPH_TYPES):
            # Make the plot transparent, so the background configured by
            # JavaScript shines through.
            figure = cast("plotly.graph_objects.Figure", copy.copy(figure))
            figure.update_layout(
                {
                    "plot_bgcolor": "rgba(0,0,0,0)",
                    "paper_bgcolor": "rgba(0,0,0,0)",
                }
            )

            plot = {
                "type": "plotly",
                "json": figure.to_json(),
            }
        else:
            figure = cast("matplotlib.figure.Figure", figure)

            file = io.BytesIO()
            figure.savefig(file, format="png", transparent=True, bbox_inches="tight")

            plot = {
                "type": "matplotlib",
                "image": base64.b64encode(file.getbuffer()).decode(),
            }

        return {
            "plot": plot,
            "boxStyle": box_style._serialize(self.session),
        }


Plot._unique_id = "Plot-builtin"
