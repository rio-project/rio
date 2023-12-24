from typing import *  # type: ignore

import rio

from . import component_details


class TreePage(rio.Component):
    _selected_component_id: Optional[int] = None

    def _on_select_component(self, component_id: int) -> None:
        self._selected_component_id = component_id

    def build(self) -> rio.Component:
        margin = 1

        children = [
            rio.Text(
                "Component Tree",
                style="heading2",
                margin=margin,
                align_x=0,
            ),
            # TODO: Scrolling
            rio.components.component_tree.ComponentTree(
                width=22,
                height="grow",
                margin=margin,
                on_select_component=self._on_select_component,
            ),
        ]

        if self._selected_component_id is not None:
            children.append(
                component_details.ComponentDetails(
                    component_id=self._selected_component_id,
                    margin=margin,
                )
            )

        return rio.Column(*children)
