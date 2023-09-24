from __future__ import annotations

from dataclasses import KW_ONLY, field
from typing import *  # type: ignore

import rio

from . import widget_base

__all__ = [
    "Router",
]


class Router(widget_base.Widget):
    _: KW_ONLY

    fallback_build: Optional[Callable[[], rio.Widget]] = None

    # Routers must not be reconciled completely, because doing so would prevent
    # a rebuild. Rebuilds are necessary so routers can update their location in
    # the widget tree.
    #
    # This value will never compare equal to that of any other router,
    # preventing reconciliation.
    _please_do_not_reconcile_me: object = field(
        init=False,
        default_factory=object,
    )

    # How many other routers are above this one in the widget tree. Zero for
    # top-level routers, 1 for the next level, and so on.
    #
    # This is stored in a list so that modifications don't trigger a rebuild.
    _level: List[int] = field(
        init=False,
        default_factory=lambda: [-1],
    )

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

        # Fetch the route instance
        try:
            route = self.session._active_route_instances[level]
        except IndexError:
            if self.fallback_build is None:
                build_callback = lambda: rio.Text("TODO: No such route")
            else:
                build_callback = self.fallback_build
        else:
            build_callback = route.build

        # Build the child
        return build_callback()
