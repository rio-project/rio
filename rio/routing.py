from __future__ import annotations

import logging
from dataclasses import KW_ONLY, dataclass, field
from typing import *  # type: ignore

import rio

from .errors import NavigationFailed


@dataclass(frozen=True)
class Page:
    page_url: str
    build: Callable[[], rio.Component]
    _: KW_ONLY
    children: List["Page"] = field(default_factory=list)
    guard: Optional[Callable[[rio.Session], Union[None, rio.URL, str]]] = None

    @property
    def segements(self) -> Tuple[str, ...]:
        page_url = self.page_url.strip("/")

        if page_url:
            return tuple(self.page_url.split("/"))

        return tuple()


class PageRedirect(Exception):
    """
    Internal exception solely used internally by `_check_page_guards`. You
    should never see this exception pop up anywhere outside of that function.
    """

    def __init__(self, redirect: rio.URL):
        self.redirect = redirect


def check_page_guards(
    sess: rio.Session,
    target_url_relative: rio.URL,
    target_url_absolute: rio.URL,
) -> Tuple[List[Page], rio.URL]:
    """
    Check whether navigation to the given target URL is possible.

    This finds the pages that would be activated by this navigation and runs
    their guards. If the guards effect a redirect, it instead attempts to
    navigate to the redirect target, and so on.

    Raises `NavigationFailed` if navigation to the target URL is not possible
    because of an error, such as an exception in a guard.

    If the URL points to a page which doesn't exist that is not considered an
    error. The result will still be valid. That is because navigation is
    possible, it's just that some PageViews will display a 404 page.

    This function does not perform any actual navigation. It simply checks
    whether navigation to the target page is possible.
    """

    assert not target_url_relative.is_absolute(), target_url_relative
    assert target_url_absolute.is_absolute(), target_url_absolute

    # Is any guard opposed to this page?
    initial_target_url = target_url_absolute
    visited_redirects = {target_url_absolute}
    past_redirects = [target_url_absolute]

    def check_guard(
        pages: Iterable[rio.Page],
        remaining_segments: Tuple[str, ...],
    ) -> List[Page]:
        # Get the page responsible for this segment
        try:
            page_segment = remaining_segments[0]
        except IndexError:
            page_segment = ""

        for page in pages:
            if page.page_url == page_segment:
                break
        else:
            return []

        # Run the guard
        if page.guard is not None:
            try:
                redirect_page = page.guard(sess)
            except Exception as err:
                raise NavigationFailed("Uncaught exception in page guard") from err

            # If a redirect was requested stop recursing
            if isinstance(redirect_page, str):
                redirect_page = rio.URL(redirect_page)

            if isinstance(redirect_page, rio.URL):
                redirect_page = sess.active_page_url.join(redirect_page)

            if redirect_page is not None and redirect_page != target_url_absolute:
                raise PageRedirect(redirect_page)

        # Recurse into the children
        sub_pages = check_guard(page.children, remaining_segments[1:])
        return [page] + sub_pages

    while True:
        # Find all pages which would by activated by this navigation, and
        # check their guards
        try:
            page_stack = check_guard(sess.app.pages, target_url_relative.parts)

        # Redirect
        except PageRedirect as err:
            redirect = err.redirect

        # Done
        else:
            return page_stack, target_url_absolute

        assert redirect.is_absolute(), redirect

        # Detect infinite loops and break them
        if redirect in visited_redirects:
            page_strings = [str(page_url) for page_url in past_redirects + [redirect]]
            page_strings_list = "\n -> ".join(page_strings)

            message = f"Rejecting navigation to `{initial_target_url}` because page guards have created an infinite loop:\n\n    {page_strings_list}"
            logging.warning(message)
            raise NavigationFailed(message)

        # Remember that this page has been visited before
        visited_redirects.add(redirect)
        past_redirects.append(redirect)

        # Rinse and repeat
        target_url_absolute = redirect
