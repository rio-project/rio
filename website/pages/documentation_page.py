from typing import *  # type: ignore
from typing import Any  # type: ignore

import rio
import rio_docs
from rio.components.component_base import Component

from .. import components as comps
from .. import structure, theme


class Outliner(rio.Component):
    @rio.event.on_page_change
    async def _on_page_change(self) -> Any:
        await self.force_refresh()

    def build(self) -> rio.Component:
        chapter_expanders = []

        # Which page is currently selected?
        try:
            active_segment = self.session.active_page_url.parts[2]
        except IndexError:
            active_segment = ""

        for section in structure.DOCUMENTATION_STRUCTURE:
            # `None` is used to represent whitespace
            if section is None:
                chapter_expanders.append(rio.Spacer(height=3))
                continue

            # Otherwise, it's a tuple of (title, articles)
            title, arts = section
            entries = {}

            # ... where each article is either a tuple of (name, url_segment,
            # article), or a rio `Component`
            for art in arts:
                if isinstance(art, tuple):
                    name, url_segment, _ = art
                else:
                    name = art.__name__
                    url_segment = name

                # TODO: Select the appropriate entry
                # Highlight the button as active?
                try:
                    part = self.session.active_page_url.parts[2]
                except IndexError:
                    part = ""
                is_active = part == url_segment

                # Create the button
                entries[name] = url_segment

            chapter_expanders.append(
                rio.Revealer(
                    title,
                    rio.SwitcherBar(
                        entries,
                        selected_value=active_segment
                        if active_segment in entries
                        else None,
                        on_change=lambda ev: self.session.navigate_to(
                            f"/documentation/{ev.value}"
                        ),
                        orientation="vertical",
                        color="primary",
                        width="grow",
                    ),
                ),
            )

        return rio.Card(
            child=rio.Column(
                *chapter_expanders,
                width=13,
                align_y=0,
                margin=1.5,
            ),
            corner_radius=(
                0,
                theme.THEME.corner_radius_large,
                theme.THEME.corner_radius_large,
                0,
            ),
            elevate_on_hover=True,
            colorize_on_hover=True,
            align_y=0,
        )


class DocumentationPage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Overlay(
                Outliner(
                    align_x=0,
                    align_y=0.4,
                ),
            ),
            rio.PageView(
                margin_top=3,
                width="grow",
                height="grow",
            ),
        )
