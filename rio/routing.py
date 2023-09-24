from __future__ import annotations

import logging
from dataclasses import KW_ONLY, dataclass, field
from typing import *  # type: ignore

import rio

from .errors import NavigationFailed


@dataclass(frozen=True)
class Route:
    route_url: str
    build: Callable[[], rio.Widget]
    _: KW_ONLY
    children: List["Route"] = field(default_factory=list)
    guard: Optional[Callable[[rio.Session], Union[None, rio.URL, str]]] = None

    @property
    def segements(self) -> Tuple[str, ...]:
        route_url = self.route_url.strip("/")

        if route_url:
            return tuple(self.route_url.split("/"))

        return tuple()


class RouteRedirect(Exception):
    """
    Internal exception solely used internally by `_check_route_guards`. You
    should never see this exception pop up anywhere outside of that function.
    """

    def __init__(self, redirect: rio.URL):
        self.redirect = redirect


def check_route_guards(
    sess: rio.Session,
    target_url_relative: rio.URL,
    target_url_absolute: rio.URL,
) -> Tuple[List[Route], rio.URL]:
    """
    Check whether navigation to the given target URL is possible.

    This finds the routes that would be activated by this navigation and runs
    their guards. If the guards effect a redirect, it instead attempts to
    navigate to the redirect target, and so on.

    Raises `NavigationFailed` if navigation to the target URL is not possible
    because of an error, such as an exception in a guard.

    If the URL points to a route which doesn't exist that is not considered an
    error. The result will still be valid. That is because navigation is
    possible, it's just that some router(s) will display a 404 page.

    This function does not perform any actual navigation. It simply checks
    whether navigation to the target route is possible.
    """

    assert not target_url_relative.is_absolute(), target_url_relative
    assert target_url_absolute.is_absolute(), target_url_absolute

    # Is any guard opposed to this route?
    initial_target_url = target_url_absolute
    visited_redirects = {target_url_absolute}
    past_redirects = [target_url_absolute]

    def check_guard(
        routes: Iterable[rio.Route],
        remaining_segments: Tuple[str, ...],
    ) -> List[Route]:
        # Get the route responsible for this segment
        try:
            route_segment = remaining_segments[0]
        except IndexError:
            route_segment = ""

        for route in routes:
            if route.route_url == route_segment:
                break
        else:
            return []

        # Run the guard
        if route.guard is not None:
            try:
                redirect_route = route.guard(sess)
            except Exception as err:
                raise NavigationFailed("Uncaught exception in route guard") from err

            # If a redirect was requested stop recursing
            if isinstance(redirect_route, str):
                redirect_route = rio.URL(redirect_route)

            if isinstance(redirect_route, rio.URL):
                redirect_route = sess.active_route.join(redirect_route)

            if redirect_route is not None and redirect_route != target_url_absolute:
                raise RouteRedirect(redirect_route)

        # Recurse into the children
        sub_routes = check_guard(route.children, remaining_segments[1:])
        return [route] + sub_routes

    while True:
        # Find all routes which would by activated by this navigation, and
        # check their guards
        try:
            route_stack = check_guard(sess.app.routes, target_url_relative.parts)

        # Redirect
        except RouteRedirect as err:
            redirect = err.redirect

        # Done
        else:
            return route_stack, target_url_absolute

        assert redirect.is_absolute(), redirect

        # Detect infinite loops and break them
        if redirect in visited_redirects:
            route_strings = [
                str(route_url) for route_url in past_redirects + [redirect]
            ]
            route_strings_list = "\n -> ".join(route_strings)

            message = f"Rejecting navigation to `{initial_target_url}` because route guards have created an infinite loop:\n\n    {route_strings_list}"
            logging.warning(message)
            raise NavigationFailed(message)

        # Remember that this route has been visited before
        visited_redirects.add(redirect)
        past_redirects.append(redirect)

        # Rinse and repeat
        target_url_absolute = redirect
