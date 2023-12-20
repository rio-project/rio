import rio

from . import component_details, component_tree


class TreePage(rio.Component):
    def build(self) -> rio.Component:
        margin = 1

        return rio.Column(
            rio.Text(
                "Component Tree",
                style="heading2",
                margin=margin,
                align_x=0,
            ),
            # TODO: Scrolling
            component_tree.ComponentTree(
                width=22,
                height="grow",
            ),
            component_details.ComponentDetails(
                margin=margin,
            ),
        )
