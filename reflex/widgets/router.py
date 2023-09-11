from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import *  # type: ignore

import reflex as rx

from . import widget_base

__all__ = [
    "RouteChangeEvent",
    "Route",
    "Router",
]


@dataclass
class RouteChangeEvent:
    previous_route: str
    new_route: str


@dataclass(frozen=True)
class Route:
    fragment_name: str
    build_function: Callable[[], rx.Widget]

    # TODO: Support guards, so users can e.g. be kicked out of a route if they
    # are not logged in
    # guard: Callable[[], Optional[str]] = lambda: ""


FALLBACK_ROUTE = Route(
    fragment_name="",
    # TODO: build a nice error page
    build_function=lambda: rx.Card(
        child=rx.Text("The page you requested could not be found."),
        height=4,
        width=12,
        align_x=0.5,
        align_y=0.4,
    ),
)


class Router(widget_base.Widget):
    routes: Dict[str, Route]
    fallback_route: Optional[Route]
    on_route_change: rx.EventHandler[RouteChangeEvent]

    # Routers must not be reconciled completely, because doing so would prevent
    # a rebuild. This value will never compare equal to that of any other
    # router, preventing reconciliation.
    _please_do_not_reconcile_me: object

    # Keeps track of the currently active route
    #
    # This is stored in a list to avoid a refresh when the route changes.
    #
    # The list is initialized in the `build` method. Until then it has zero
    # values. Once initialized, it contains a single string.
    _current_route_name: List[str]

    def __init__(
        self,
        *routes: Route,
        fallback_route: Optional[Route] = None,
        on_route_change: rx.EventHandler[RouteChangeEvent] = None,
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
        self.on_route_change = on_route_change
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

    def _on_route_change(self) -> None:
        """
        Called by the session when the route changes.
        """
        # Dirty the router. This relies on some other widget to trigger a
        # refresh
        self.session._register_dirty_widget(
            self,
            include_fundamental_children_recursively=False,
        )

    def _find_router_level(self) -> int:
        """
        Follow the chain of `_weak_builder_` references to find how deep in the
        hierarcy of routers this one is. Returns 0 for a top-level router, 1
        for a router inside a router, etc.
        """
        # Register with the session
        #
        # This really should be done only once, and earlier, but the session
        # isn't available yet in `__init__`
        self.session._route_change_listeners.add(self)

        # TODO / FIXME: This would be nice to cache - store the level in each
        # router, then only look far enough to reach the parent. The problem
        # with this approach is, that this router may be rebuilt before its
        # parent.

        level = 0
        cur_weak = self._weak_builder_

        while cur_weak is not None:
            cur = cur_weak()

            # Possible if this router has been removed from the widget tree
            if cur is None:
                break

            # Found it
            if isinstance(cur, Router):
                level += 1

            # Chain up
            cur_weak = cur._weak_builder_

        return level

    def build(self) -> rx.Widget:
        # Look up the parent router
        level = self._find_router_level()

        # Determine the route fragment
        try:
            new_route_fragment = self.session._current_route[level]
        except IndexError:
            new_route_fragment = ""

        # Keep track of it
        if not self._current_route_name:
            self._current_route_name.append(new_route_fragment)
        else:
            old_route_fragment = self._current_route_name[0]
            self._current_route_name[0] = new_route_fragment

            # Trigger the route change event
            if old_route_fragment != new_route_fragment:
                asyncio.create_task(
                    self._call_event_handler(
                        self.on_route_change,
                        RouteChangeEvent(
                            previous_route=old_route_fragment,
                            new_route=new_route_fragment,
                        ),
                    )
                )

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
