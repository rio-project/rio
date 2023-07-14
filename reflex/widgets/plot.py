from __future__ import annotations

from typing import *  # type: ignore

from reflex.common import Jsonable

from . import widget_base

try:
    import plotly
    import plotly.graph_objects
except ImportError:
    if TYPE_CHECKING:
        import plotly


__all__ = ["Plot"]


class Plot(widget_base.HtmlWidget):
    figure: plotly.graph_objects.Figure

    def _custom_serialize(self) -> Dict[str, Jsonable]:
        return {"plotJson": self.figure.to_json()}


Plot._unique_id = "Plot-builtin"
