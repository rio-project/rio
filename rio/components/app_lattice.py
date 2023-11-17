from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from . import class_container, component_base

__all__ = [
    "AppLattice",
]


class AppTopBar(component_base.Component):
    def build(self) -> rio.Component:
        thm = self.session.attachments[rio.Theme]

        icons = []
        for icon in ("castle", "error", "archive"):
            icons.append(rio.Icon(icon, width=2, height=2))

        return class_container.ClassContainer(
            child=rio.Row(
                rio.Icon(
                    "menu",
                    width=2,
                    height=2,
                    margin_right=1,
                ),
                rio.Text(
                    self.session.app.name,
                    style=rio.TextStyle(
                        font_size=1.8,
                        fill=thm.primary_palette.foreground,
                    ),
                ),
                rio.Spacer(),
                rio.Row(*icons, spacing=2),
            ),
            classes=["rio-switcheroo-primary"],
            margin=1,
        )


class Sidebar(component_base.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Row(
                rio.Icon(
                    "menu-open",
                    width=2,
                    height=2,
                    align_y=0,
                ),
                rio.Column(
                    rio.Text(
                        self.session.app.name,
                        style="heading2",
                        align_x=0,
                    ),
                    rio.Text(
                        "TODO: Subtext",
                        style="text",
                        align_x=0,
                    ),
                    align_y=0,
                ),
                spacing=1,
                margin_x=1,
                margin_y=1,
                align_x=0,
            ),
            rio.SwitcherBar(
                {
                    "Foo": "foo",
                    "Bar": "bar",
                },
                orientation="vertical",
                width=25,
                margin=2,
                color="primary",
            ),
            rio.Spacer(),
            rio.SwitcherBar(
                {
                    "Settings": "settings",
                },
                orientation="vertical",
                width=25,
                margin=2,
                color="primary",
            ),
        )


class AppLattice(component_base.Component):
    _: KW_ONLY

    fallback_build: Optional[Callable[[], rio.Component]] = None

    def build(self) -> rio.Component:
        thm = self.session.attachments[rio.Theme]

        return rio.Drawer(
            anchor=rio.Stack(
                rio.Rectangle(
                    style=rio.BoxStyle(
                        fill=thm.primary_palette.background,
                    ),
                ),
                rio.Column(
                    AppTopBar(),
                    rio.Card(
                        rio.Stack(
                            rio.PageView(
                                fallback_build=self.fallback_build,
                            ),
                            rio.CircularButton(
                                "castle",
                                align_x=1,
                                align_y=1,
                            ),
                        ),
                        corner_radius=(
                            thm.corner_radius_medium,
                            thm.corner_radius_medium,
                            0,
                            0,
                        ),
                        height="grow",
                    ),
                ),
            ),
            content=Sidebar(),
        )
