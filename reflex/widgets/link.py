from __future__ import annotations

from typing import *  # type: ignore

from uniserde import JsonDoc

import reflex as rx

from .. import app_server, common
from . import widget_base

__all__ = [
    "Link",
]


class Link(widget_base.FundamentalWidget):
    # Exactly one of these will be set, the other `None`
    child_text: Optional[str]
    child_widget: Optional[widget_base.Widget]

    link: Union[str, rx.URL]

    # The serializer can't handle Union types. Override the constructor, so it
    # splits the child into two values
    def __init__(
        self,
        child: Union[str, rx.Widget],
        link: Union[str, rx.URL],
        *,
        spacing: float = 0.0,
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

        if isinstance(child, str):
            self.child_text = child
            self.child_widget = None
        else:
            self.child_text = None
            self.child_widget = child

        self.link = link

    async def _on_message(self, msg: Any) -> None:
        assert isinstance(msg, dict), msg

        # Navigate to the link. Note that this allows the client to inject a,
        # possibly malicious, link. This is fine, because the client can do so
        # anyway, simply by changing the URL in the browser. Thus the server
        # has to be equipped to handle malicious routes anyway.
        target_route = msg["route"]
        self.session.navigate_to(target_route)

    def _custom_serialize(self, server: app_server.AppServer) -> JsonDoc:
        # Is the link a URL or route?
        if isinstance(self.link, rx.URL):
            link = str(self.link)
            is_route = False
        elif self.link.startswith(("/", "./", "../")):
            full_route = common.join_routes(self.session.current_route, self.link)
            link = "/" + "/".join(full_route)
            is_route = True
        else:
            link = self.link
            is_route = True

        return {
            "link": link,
            "is_route": is_route,
        }


Link._unique_id = "Link-builtin"
