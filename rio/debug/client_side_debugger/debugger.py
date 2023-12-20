import rio

from . import tree_page


class ClientSideDebugger(rio.Component):
    def build(self) -> rio.Component:
        return rio.Row(
            # Big fat line to separate the debugger from the rest of the page
            rio.Rectangle(
                width=0.4,
                style=rio.BoxStyle(fill=self.session.theme.primary_palette.background),
            ),
            # Currently active page
            rio.components.class_container.ClassContainer(
                # TODO: Allow switching pages
                tree_page.TreePage(),
                classes=["rio-debugger-background"],
            ),
            # Navigation
            rio.Column(
                rio.SwitcherBar(
                    ["foo", "bar", "baz"],
                    orientation="vertical",
                ),
                rio.Spacer(),
                rio.Text("Rio"),
                width=3.5,
            ),
        )
