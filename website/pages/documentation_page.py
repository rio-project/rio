from typing import *  # type: ignore
from typing import Any  # type: ignore

import rio

from .. import structure, theme


class Outliner(rio.Component):
    @rio.event.on_page_change
    async def _on_page_change(self) -> Any:
        await self.force_refresh()

    def build(self) -> rio.Component:
        docs_page = self.session.active_page_instances[0]

        print()
        for child in docs_page.children:
            print(child.page_url)

        if not docs_page.children:
            return rio.Spacer(width=0, height=0)

        sub_names = []
        sub_urls = []
        for page in docs_page.children:
            sub_names.append(page.page_url.replace("-", " ").capitalize())
            sub_urls.append(page.page_url)

        return rio.Column(
            rio.Text("Current Section", style="heading2"),
            rio.Card(
                rio.SwitcherBar(
                    names=sub_names,
                    values=sub_urls,
                    selected_value="placeholder",
                    color="primary",
                    orientation="vertical",
                ),
            ),
            rio.IconButton(
                icon="arrow-back",
                on_press=lambda: self.session.navigate_to("/documentation"),
                color="primary",
                align_x=0.5,
            ),
            spacing=1,
        )

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
        # Find the currently active section
        active_segment = self.session.active_page_url.parts[1]

        try:
            section_name = structure.DOCUMENTATION_URL_SEGMENT_TO_SECTION[
                active_segment
            ]
        except KeyError:
            section_name = None

        return rio.Row(
            Outliner(
                margin_left=1,
                align_y=0.5,
            ),
            rio.PageView(
                width="grow",
                height="grow",
            ),
            spacing=2,
            margin_top=3,
        )
