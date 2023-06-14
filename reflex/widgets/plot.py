from __future__ import annotations

from dataclasses import KW_ONLY
import io
from typing import Dict
import plotly
import plotly.graph_objects
from abc import ABC, abstractmethod

from reflex.common import Jsonable

from . import widget_base

__all__ = ["Plot"]


class Plot(widget_base.HtmlWidget):
    figure: plotly.graph_objects.Figure

    def _custom_serialize(self) -> Dict[str, Jsonable]:
        return {"plotJson": self.figure.to_json()}


Plot._unique_id = "Plot-builtin"
