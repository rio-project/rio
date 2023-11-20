from __future__ import annotations

from dataclasses import KW_ONLY, field
from typing import *  # type: ignore

import rio

from . import component_base

__all__ = [
    "PageView",
]


def default_fallback_build(sess: rio.Session) -> rio.Component:
    thm = sess.theme

    return rio.Column(
        rio.Row(
            rio.Icon(
                "material/error",
                fill="warning",
                width=4,
                height=4,
            ),
            rio.Text(
                "This page does not exist",
                style=rio.TextStyle(
                    font_size=3,
                    fill=thm.warning_palette.background,
                ),
            ),
            spacing=2,
            align_x=0.5,
        ),
        rio.Text(
            "The URL you have entered does not exist on this website. Double check your spelling, or try navigating to the home page.",
            multiline=True,
        ),
        rio.Button(
            "Take me home",
            on_press=lambda: sess.navigate_to("/"),
        ),
        spacing=3,
        width=20,
        align_x=0.5,
        align_y=0.35,
    )


class PageView(component_base.Component):
    """
    Placeholders for pages.

    Rio apps can consist of many pages. You might have a welcome page, a
    settings page, a login, and so on. Page views act as placeholders, that
    don't have an appearance of their own, but instead look up the currently
    active page, and display that.

    A minimal example:

    ```python
    import rio

    app = rio.App(
        build=lambda: rio.Column(
            rio.Text("Welcome to my page!"), rio.PageView(
                width="grow", height="grow",
            ),
        ), pages=[
            rio.Page(
                "", build=lambda: rio.Text("This is the home page"),
            ), rio.Page(
                "subpage", build=lambda: rio.Text("This is a subpage"),
            ),
        ],
    )

    app.run_in_browser()
    ```

    This will display "This is the home page" when navigating to the root URL,
    but "This is a subpage" when navigating to "/subpage". Note that on both
    pages the text "Welcome to my page!" is displayed above the page content.
    That's because it's not part of the `PageView`.

    # TODO: Link to the routing/multipage how-to page

    Attributes:
        fallback_build: A callback that is called if the current URL does not
            correspond to any page in the application. It should return a Rio
            component that is displayed instead. If not specified Rio will
            display a default error page.
    """

    _: KW_ONLY

    fallback_build: Optional[Callable[[], rio.Component]] = None

    # PageViews must not be reconciled completely, because doing so would prevent
    # a rebuild. Rebuilds are necessary so PageViews can update their location in
    # the component tree.
    #
    # This value will never compare equal to that of any other PageView,
    # preventing reconciliation.
    _please_do_not_reconcile_me: object = field(
        init=False,
        default_factory=object,
    )

    # How many other PageViews are above this one in the component tree. Zero for
    # top-level PageViews, 1 for the next level, and so on.
    #
    # This is stored in a list so that modifications don't trigger a rebuild.
    _level: List[int] = field(
        init=False,
        default_factory=lambda: [-1],
    )

    def _find_page_view_level_and_track_in_session(self) -> int:
        """
        Follow the chain of `_weak_builder_` references to find how deep in the
        hierarchy of PageViews this one is. Returns 0 for a top-level PageView, 1
        for a PageView inside a PageView, etc.

        Furthermore, this updates the session's `_page_views` dictionary to track
        the parent PageView of this one.
        """

        # Determine how many PageViews are above this one
        #
        # TODO / FIXME: This would be nice to cache - store the level in each
        # PageView, then only look far enough to reach the parent. The problem
        # with this approach is, that this PageView may be rebuilt before its
        # parent.
        level = 0
        parent: Optional[PageView] = None
        cur_weak = self._weak_builder_

        while cur_weak is not None:
            cur = cur_weak()

            # Possible if this PageView has been removed from the component tree
            if cur is None:
                break

            # Found it
            if isinstance(cur, PageView):
                level += 1

                if parent is None:
                    parent = cur

            # Chain up
            cur_weak = cur._weak_builder_

        # Update the PageView's level
        self._level[0] = level

        # Track the parent PageView in the session
        self.session._page_views[self] = None if parent is None else parent._id

        return level

    def build(self) -> rio.Component:
        # Look up the parent PageView
        level = self._find_page_view_level_and_track_in_session()

        # Fetch the page instance
        try:
            page = self.session._active_page_instances[level]
        except IndexError:
            if self.fallback_build is None:
                build_callback = lambda sess=self.session: default_fallback_build(sess)
            else:
                build_callback = self.fallback_build
        else:
            build_callback = page.build

        # Build the child
        return build_callback()
