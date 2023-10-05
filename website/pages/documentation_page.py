from typing import *  # type: ignore
from typing import Any  # type: ignore

import rio
import rio_docs
from rio.components.component_base import Component

from .. import components as comps
from .. import structure, theme


class Outliner(rio.Component):
    @rio.event.on_route_change
    async def on_route_change(self) -> Any:
        await self.force_refresh()

    def build(self) -> rio.Component:
        chapter_expanders = []

        for section in structure.DOCUMENTATION_STRUCTURE:
            # `None` is used to represent whitespace
            if section is None:
                chapter_expanders.append(rio.Spacer(height=3))
                continue

            # Otherwise, it's a tuple of (title, articles)
            title, arts = section
            buttons = []

            # ... where each article is either a tuple of (name, url_segment,
            # article), or a rio `Widget`
            for art in arts:
                if isinstance(art, tuple):
                    name, url_segment, _ = art
                else:
                    name = art.__name__
                    url_segment = name

                # Highlight the button as active?
                try:
                    part = self.session.active_route.parts[2]
                except IndexError:
                    part = ""
                is_active = part == url_segment

                # Create the button
                buttons.append(
                    rio.Button(
                        name,
                        color=theme.THEME.primary_color.replace(opacity=0.3)
                        if is_active
                        else rio.Color.TRANSPARENT,
                        on_press=lambda _, segment=url_segment: self.session.navigate_to(
                            f"/documentation/{segment}"
                        ),
                    ),
                )

            chapter_expanders.append(
                rio.Revealer(
                    title,
                    rio.Column(
                        *buttons,
                        spacing=theme.THEME.base_spacing,
                    ),
                ),
            )

        return rio.Card(
            child=rio.Column(
                *chapter_expanders,
                width=13,
                align_y=0,
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
            rio.Sticky(
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
