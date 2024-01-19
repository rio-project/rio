from typing import *  # type: ignore

import rio

from . import (
    ai_chat_page,
    deploy_page,
    docs_page,
    icons_page,
    project_page,
    theme_picker_page,
    tree_page,
)


class ClientSideDebugger(rio.Component):
    selected_page: Literal[
        "project",
        "tree",
        "docs",
        "ai-chat",
        "deploy",
    ] | None = None

    def get_selected_page(self) -> rio.Component | None:
        PAGE_WIDTH = 22

        # Nothing selected
        if self.selected_page is None:
            return None

        # Project
        if self.selected_page == "project":
            return project_page.ProjectPage(
                width=PAGE_WIDTH,
            )

        # Tree
        if self.selected_page == "tree":
            return tree_page.TreePage(
                width=PAGE_WIDTH,
            )

        # Icons
        if self.selected_page == "icons":
            return icons_page.IconsPage(
                width=PAGE_WIDTH,
            )

        # Theme
        if self.selected_page == "theme":
            return theme_picker_page.ThemePickerPage(
                width=35,
            )

        # Docs
        if self.selected_page == "docs":
            return docs_page.DocsPage(
                width=PAGE_WIDTH,
            )

        # AI Chat
        if self.selected_page == "ai-chat":
            return ai_chat_page.AIChatPage(
                width=PAGE_WIDTH,
            )

        # Deploy
        if self.selected_page == "deploy":
            return deploy_page.DeployPage(
                width=PAGE_WIDTH,
            )

        # Anything else / TODO
        return rio.Text(
            f"TODO: {self.selected_page}",
            margin=2,
            width=PAGE_WIDTH,
        )

    def build(self) -> rio.Component:
        return rio.Row(
            # Big fat line to separate the debugger from the rest of the page
            rio.Rectangle(
                width=0.4,
                style=rio.BoxStyle(fill=self.session.theme.primary_palette.background),
            ),
            # Currently active page
            rio.components.class_container.ClassContainer(
                rio.Switcher(self.get_selected_page()),
                classes=["rio-switcheroo-neutral", "rio-debugger-background"],
            ),
            # Navigation
            rio.Column(
                rio.SwitcherBar(
                    names=[
                        "Project",
                        "Tree",
                        "Icons",
                        "Theme",
                        "Docs",
                        "AI",
                        "Deploy",
                    ],
                    icons=[
                        # "home",
                        "rio/logo:outline",
                        "view-quilt",
                        "emoji-people",
                        "palette",
                        "library-books",
                        "chat-bubble",
                        "rocket-launch",
                    ],
                    values=[
                        "project",
                        "tree",
                        "icons",
                        "theme",
                        "docs",
                        "ai-chat",
                        "deploy",
                    ],
                    allow_none=True,
                    orientation="vertical",
                    spacing=2,
                    color="primary",
                    selected_value=ClientSideDebugger.selected_page,
                    margin=0.3,
                ),
                rio.Spacer(),
                rio.components.debugger_connector.DebuggerConnector(),
            ),
        )
