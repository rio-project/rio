from typing import *  # type: ignore

import reflex as rx
from .. import theme

from .. import components as comps


OUTLINE = {
    "Introduction": (
        "What is Reflex?",
        "Why Reflex?",
        "How does Reflex work?",
    ),
    "Getting Started": (
        "Installation",
        "Hello World",
        "Widgets",
        "Layouts",
    ),
    "Advanced": (
        "Styling",
        "Events",
        "Animations",
        "Reflex CLI",
    ),
}


class DocumentationView(rx.Widget):
    def build(self) -> rx.Widget:
        # Build the outliner
        chapter_expanders = []

        for chapter, sections in OUTLINE.items():
            buttons = [
                rx.Button(
                    section,
                    color=rx.Color.TRANSPARENT,
                    on_press=lambda _: self.session.navigate_to(f"./{section}"),
                )
                for section in sections
            ]

            chapter_expanders.append(
                rx.Revealer(
                    chapter,
                    rx.Column(
                        *buttons,
                        spacing=theme.THEME.base_spacing,
                    ),
                ),
            )

        # Combine everything
        return rx.Column(
            comps.NavigationBarDeadSpace(),
            rx.Row(
                rx.Column(
                    *chapter_expanders,
                    margin_left=3,
                    width=20,
                    align_y=0,
                ),
                rx.Router(
                    rx.Route(
                        "",
                        lambda: rx.Text(
                            "Documentation Page",
                            width="grow",
                            height="grow",
                        ),
                    ),
                    width="grow",
                    height="grow",
                ),
                height="grow",
            ),
        )
