from __future__ import annotations

import copy
import io
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .. import maybes
from ..debug import ModuleProxy
from . import component_base

if TYPE_CHECKING:
    import matplotlib.figure  # type: ignore
    import plotly.graph_objects  # type: ignore
else:
    # Required for runtime type checking
    matplotlib = ModuleProxy("matplotlib.figure")
    plotly = ModuleProxy("plotly.graph_objects")


__all__ = ["Plot"]


class Plot(component_base.FundamentalComponent):
    """
    Displays a graph.


    Attributes:
        figure: The `plotly` figure to display.

        style: Controls the appearance of the plot. The following attributes are supported:
            - `fill`
            - `corner_radius`

        Any other attributes are ignored at this time.
    """

    figure: matplotlib.figure.Figure | plotly.graph_objects.Figure
    background: Optional[rio.Fill]
    corner_radius: Union[float, Tuple[float, float, float, float]]

    def __init__(
        self,
        figure: matplotlib.figure.Figure | plotly.graph_objects.Figure,
        *,
        background: Optional[rio.FillLike] = None,
        corner_radius: Union[float, Tuple[float, float, float, float]] = 0,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["natural", "grow"], float] = "natural",
        height: Union[Literal["natural", "grow"], float] = "natural",
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        super().__init__(
            key=key,
            margin=margin,
            margin_x=margin_x,
            margin_y=margin_y,
            margin_left=margin_left,
            margin_top=margin_top,
            margin_right=margin_right,
            margin_bottom=margin_bottom,
            width=width,
            height=height,
            align_x=align_x,
            align_y=align_y,
        )

        self.figure = figure
        self.background = None if background is None else rio.Fill._try_from(background)
        self.corner_radius = corner_radius

    def _custom_serialize(self) -> JsonDoc:
        # Figure
        figure = self.figure
        plot: JsonDoc
        if isinstance(figure, maybes.PLOTLY_GRAPH_TYPES):
            # Make the plot transparent, so `self.background` shines through.
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
            figure.savefig(file, format="svg", transparent=True, bbox_inches="tight")

            plot = {
                "type": "matplotlib",
                "svg": bytes(file.getbuffer()).decode("utf-8"),
            }

        # Corner radius
        if isinstance(self.corner_radius, (int, float)):
            corner_radius = (self.corner_radius,) * 4
        else:
            corner_radius = self.corner_radius

        # Combine everything
        return {
            "plot": plot,
            "corner_radius": corner_radius,
        }


Plot._unique_id = "Plot-builtin"
