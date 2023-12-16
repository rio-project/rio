from __future__ import annotations

from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .. import common
from . import component_base

__all__ = [
    "Link",
]


class Link(component_base.FundamentalComponent):
    """
    Navigates to a page or URL when clicked.

    `Link`s display a short text, or arbitrary component, and navigate to a page
    or URL when clicked.
    """

    # Exactly one of these will be set, the other `None`
    child_text: Optional[str]
    child_component: Optional[component_base.Component]

    target_url: Union[rio.URL, str]

    # The serializer can't handle Union types. Override the constructor, so it
    # splits the child into two values
    def __init__(
        self,
        child: Union[str, rio.Component],
        target_url: Union[str, rio.URL],
        *,
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
        """
        Args:
            child: The text or component to display inside the link.

            target_url: The page or URL to navigate to when clicked.
        """
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
            self.child_component = None
        else:
            self.child_text = None
            self.child_component = child

        self.target_url = target_url

        self._explicitly_set_properties_.update(("child_text", "child_component"))

    async def _on_message(self, msg: Any) -> None:
        assert isinstance(msg, dict), msg

        # Navigate to the link. Note that this allows the client to inject a,
        # possibly malicious, link. This is fine, because the client can do so
        # anyway, simply by changing the URL in the browser. Thus the server
        # has to be equipped to handle malicious page URLs anyway.
        target_page = msg["page"]
        self.session.navigate_to(target_page)

    def _custom_serialize(self) -> JsonDoc:
        # Get the full URL to navigate to
        target_url_absolute = self.session.active_page_url.join(
            rio.URL(self.target_url)
        )

        # Is the link a URL or page?
        #
        # The URL is a page, if it starts with the session's base URL
        try:
            common.make_url_relative(
                self.session._base_url,
                target_url_absolute,
            )
        except ValueError:
            is_page = False
        else:
            is_page = True

        # Serialize everything
        return {
            "targetUrl": str(target_url_absolute),
            "isPage": is_page,
        }


Link._unique_id = "Link-builtin"
