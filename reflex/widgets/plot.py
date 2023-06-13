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
        # Get the URL for the hosted plotly.js library
        plotly_js_url = (
            self.session.app_server.external_url + "/reflex/asset/plotly.min.js"
        )

        # Get the HTML for the plot
        # buffer = io.StringIO()

        # self.figure.write_html(
        #     buffer,
        #     full_html=True,
        #     # include_plotlyjs=plotly_js_url,
        #     include_plotlyjs="cdn",
        #     default_width="100%",
        #     default_height="100%",
        #     validate=True,
        # )

        # html_source = buffer.getvalue()

        html_source = plotly.offline.plot(
            self.figure,
            output_type="div",
            # include_plotlyjs=False,
            include_plotlyjs="cdn",
            # default_width="100%",
            # default_height="100%",
                validate=True,
        )

        return {"htmlSource": html_source}


Plot._unique_id = "Plot-builtin"
