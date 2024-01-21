from typing import *  # type: ignore

import rio

from .. import structure


class DocsOutliner(rio.Component):
    @rio.event.on_page_change
    async def _on_page_change(self) -> None:
        await self.force_refresh()

    def _on_switcher_change(self, ev: rio.SwitcherBarChangeEvent) -> None:
        assert ev.value is not None
        self.session.navigate_to(ev.value)

    def build(self) -> rio.Component:
        try:
            section_page = self.session.active_page_instances[1]
        except IndexError:
            section_page = None
        else:
            if section_page.page_url == "":
                section_page = None

        try:
            selected_page = self.session.active_page_instances[2]
        except IndexError:
            section_page = None
            selected_page = None

        # No active section - hide
        if section_page is None:
            return rio.Spacer(width=0, height=0)

        assert selected_page is not None

        # Find the section in the structure
        for section in structure.DOCUMENTATION_STRUCTURE:
            if section is None:
                continue

            section_name, section_url, builders = section

            if section_name == section_page.name:
                break
        else:
            assert False, f'Cannot find section "{section_page.page_url}" in structure'

        # Display all pages in this section
        return rio.Column(
            rio.Text(section_name, style="heading2"),
            rio.Card(
                rio.SwitcherBar(
                    names=[b.title for b in builders],
                    values=[b.url_segment for b in builders],
                    selected_value=selected_page.page_url,
                    color="primary",
                    orientation="vertical",
                    on_change=self._on_switcher_change,
                    margin=1,
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
