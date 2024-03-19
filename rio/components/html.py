from typing import *  # type: ignore

from .component_base import FundamentalComponent

__all__ = ["Html"]


class Html(FundamentalComponent):
    """
    Renders HTML.

    `Html` allows you to embed HTML in your app. It takes HTML code as input and
    renders it. If you want to embed an entire website, use the `Website`
    component instead.

    Attributes:
        html: The HTML to render.
    """

    html: str


Html._unique_id = "Html-builtin"
