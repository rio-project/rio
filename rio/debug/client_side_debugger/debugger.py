from typing import *  # type: ignore

import rio

from . import deploy_page, docs_page, icons_page, project_page, tree_page


class ClientSideDebugger(rio.Component):
    selected_page: Literal[
        "project",
        "tree",
        "docs",
        "ai-chat",
        "deploy",
    ] | None = "ai-chat"

    def get_selected_page(self) -> rio.Component:
        # Project
        if self.selected_page == "project":
            return project_page.ProjectPage()

        # Tree
        if self.selected_page == "tree":
            return tree_page.TreePage()

        # Icons
        if self.selected_page == "icons":
            return icons_page.IconsPage()

        # Docs
        if self.selected_page == "docs":
            return docs_page.DocsPage()

        # Deploy
        if self.selected_page == "deploy":
            return deploy_page.DeployPage()

        # Anything else / TODO
        return rio.Text(
            f"TODO: {self.selected_page}",
            margin=2,
        )

    def build(self) -> rio.Component:
        current_page = None if self.selected_page is None else self.get_selected_page()

        return rio.Row(
            # Big fat line to separate the debugger from the rest of the page
            rio.Rectangle(
                width=0.4,
                style=rio.BoxStyle(fill=self.session.theme.primary_palette.background),
            ),
            # Currently active page
            rio.components.class_container.ClassContainer(
                rio.Switcher(current_page),
                classes=["rio-switcheroo-neutral", "rio-debugger-background"],
            ),
            # Navigation
            rio.Column(
                rio.SwitcherBar(
                    names=[
                        "Project",
                        "Tree",
                        "Icons",
                        "Docs",
                        "AI",
                        "Deploy",
                    ],
                    icons=[
                        "home",
                        "view-quilt",
                        "emoji-people",
                        "library-books",
                        "chat-bubble",
                        "rocket-launch",
                    ],
                    values=[
                        "project",
                        "tree",
                        "icons",
                        "docs",
                        "ai-chat",
                        "deploy",
                    ],
                    allow_none=True,
                    orientation="vertical",
                    spacing=2,
                    color="primary",
                    selected_value=ClientSideDebugger.selected_page,
                    margin_x=0.3,
                ),
                rio.Spacer(),
                rio.components.debugger_connector.DebuggerConnector(),
                width=3.5,
            ),
        )
