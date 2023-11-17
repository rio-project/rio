from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from . import component_base

__all__ = [
    "AppLattice",
]


class AppTopBar(component_base.Component):
    def build(self) -> rio.Component:
        thm = self.session.attachments[rio.Theme]

        return rio.Rectangle(
            height=4,
            style=rio.BoxStyle(
                fill=thm.primary_palette.background,
            ),
        )


class Sidebar(component_base.Component):
    def build(self) -> rio.Component:
        return rio.SwitcherBar(
            {
                "Foo": "foo",
                "Bar": "bar",
            },
            orientation="vertical",
            width=25,
            margin=2,
            color="primary",
        )


class AppLattice(component_base.Component):
    _: KW_ONLY

    fallback_build: Optional[Callable[[], rio.Component]] = None

    def build(self) -> rio.Component:
        return rio.Drawer(
            anchor=rio.Column(
                AppTopBar(),
                rio.PageView(
                    fallback_build=self.fallback_build,
                    height="grow",
                ),
            ),
            content=Sidebar(),
        )
