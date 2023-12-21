from typing import *  # type: ignore

import rio

from . import debugger_connector, deploy_page, docs_page, project_page, tree_page


class ClientSideDebugger(rio.Component):
    selected_page: Literal[
        "project",
        "tree",
        "docs",
        "ai-chat",
        "deploy",
    ] | None = None

    def get_selected_page(self) -> rio.Component:
        # No page
        if self.selected_page == None:
            return rio.Spacer(width=0, height=0)

        # Project
        if self.selected_page == "project":
            return project_page.ProjectPage()

        # Tree
        if self.selected_page == "tree":
            return tree_page.TreePage()

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
        return rio.Row(
            # Big fat line to separate the debugger from the rest of the page
            rio.Rectangle(
                width=0.4,
                style=rio.BoxStyle(fill=self.session.theme.primary_palette.background),
            ),
            # Currently active page
            rio.components.class_container.ClassContainer(
                self.get_selected_page(),
                classes=["rio-switcheroo-neutral", "rio-debugger-background"],
            ),
            # Navigation
            rio.Column(
                rio.SwitcherBar(
                    names=[
                        "Project",
                        "Tree",
                        "Docs",
                        "AI",
                        "Deploy",
                    ],
                    icons=[
                        "home",
                        "view-quilt",
                        "library-books",
                        "chat-bubble",
                        "rocket-launch",
                    ],
                    values=[
                        "project",
                        "tree",
                        "docs",
                        "ai-chat",
                        "deploy",
                    ],
                    orientation="vertical",
                    spacing=2,
                    color="primary",
                    selected_value=ClientSideDebugger.selected_page,
                ),
                rio.Spacer(),
                debugger_connector.DebuggerConnector(),
                width=3.5,
            ),
        )
