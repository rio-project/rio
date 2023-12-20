import rio

from . import component_details, component_tree


class TreePage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text("Component Tree", style="heading2"),
            # TODO: Scrolling
            component_tree.ComponentTree(
                width=22,
                height="grow",
            ),
            component_details.ComponentDetails(),
        )
