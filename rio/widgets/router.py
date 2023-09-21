from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

import rio

from . import widget_base

__all__ = [
    "Route",
    "Router",
]


@dataclass(frozen=True)
class Route:
    fragment_name: str
    build_function: Callable[[], rio.Widget]
    _: KW_ONLY
    guard: Callable[[rio.Session], Optional[str]] = lambda _: None


FALLBACK_ROUTE = Route(
    fragment_name="",
    # TODO: build a nice error page
    build_function=lambda: rio.Text(
        "The page you requested could not be found.",
        height=4,
        width=12,
        align_x=0.5,
        align_y=0.4,
    ),
)


class Router(widget_base.Widget):
    routes: Dict[str, Route]
    fallback_route: Optional[Route]

    # Routers must not be reconciled completely, because doing so would prevent
    # a rebuild. Rebuilds are necessary so routers can update their location in
    # the widget tree.
    #
    # This value will never compare equal to that of any other router,
    # preventing reconciliation.
    _please_do_not_reconcile_me: object

    # How many other routers are above this one in the widget tree. Zero for
    # top-level routers, 1 for the next level, and so on.
    #
    # This is stored in a list so that modifications don't trigger a rebuild.
    _level = [-1]

    def __init__(
        self,
        *routes: Route,
        fallback_route: Optional[Route] = None,
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

        self.routes = {}
        self.fallback_route = fallback_route
        self._please_do_not_reconcile_me = object()
        self._current_route_name = []

        # Convert the routes to a form that facilitates lookup. This is also a
        # good time for sanity checks
        for route in routes:
            if "/" in route.fragment_name:
                raise ValueError(
                    f"Route names cannot contain slashes: {route.fragment_name}",
                )

            if route.fragment_name in self.routes:
                raise ValueError(
                    f'Multiple routes share the same name "{route.fragment_name}"',
                )

            self.routes[route.fragment_name] = route

    def _find_router_level_and_track_in_session(self) -> int:
        """
        Follow the chain of `_weak_builder_` references to find how deep in the
        hierarchy of routers this one is. Returns 0 for a top-level router, 1
        for a router inside a router, etc.

        Furthermore, this updates the session's `_routers` dictionary to track
        the parent router of this one.
        """

        # Determine how many routers are above this one
        #
        # TODO / FIXME: This would be nice to cache - store the level in each
        # router, then only look far enough to reach the parent. The problem
        # with this approach is, that this router may be rebuilt before its
        # parent.
        level = 0
        parent: Optional[Router] = None
        cur_weak = self._weak_builder_

        while cur_weak is not None:
            cur = cur_weak()

            # Possible if this router has been removed from the widget tree
            if cur is None:
                break

            # Found it
            if isinstance(cur, Router):
                level += 1

                if parent is None:
                    parent = cur

            # Chain up
            cur_weak = cur._weak_builder_

        # Update the router's level
        self._level[0] = level

        # Track the parent router in the session
        self.session._routers[self] = None if parent is None else parent._id

        return level

    def build(self) -> rio.Widget:
        # Look up the parent router
        level = self._find_router_level_and_track_in_session()

        # Determine the route fragment
        try:
            new_route_fragment = self.session._current_route[level]
        except IndexError:
            new_route_fragment = ""

        # Fetch the route instance
        try:
            route = self.routes[new_route_fragment]
        except KeyError:
            if self.fallback_route is None:
                route = FALLBACK_ROUTE
            else:
                route = self.fallback_route

        # Build the child
        return route.build_function()
