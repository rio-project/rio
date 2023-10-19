from typing import *  # type: ignore
from typing import Optional

from .component_base import Component, FundamentalComponent

__all__ = ["ScrollTarget"]


class ScrollTarget(FundamentalComponent):
    """
    Allows browsers to scroll to a specific component via URL fragment.

    `ScrollTarget` is a container which can be referenced by a URL fragment,
    which allows browsers to scroll to it when the page is loaded. For example,
    if your website contains a `ScrollTarget` with the ID `"my-section"`, then a
    browser visiting `https://your.website/#my-section` will immediately scroll
    it into view.

    Attributes:
        id: The ID of the `ScrollTarget`. This must be unique among all
            `ScrollTarget`s on the page.

        child: The child component to display inside the `ScrollTarget`.
    """

    id: str
    child: Optional[Component] = None

    def __post_init__(self):
        if self.id.startswith("rio-id-"):
            raise ValueError(
                f"Invalid ID for ScrollTarget: `{self.id}`. IDs starting with"
                f"`rio-id-` are reserved for internal use."
            )


ScrollTarget._unique_id = "ScrollTarget-builtin"
