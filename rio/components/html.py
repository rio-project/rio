from typing import *  # type: ignore

from .component_base import FundamentalComponent

__all__ = ["Html"]


class Html(FundamentalComponent):
    html: str


Html._unique_id = "Html-builtin"
