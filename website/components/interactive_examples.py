from abc import ABC, abstractmethod
from typing import *  # type: ignore
from typing import Dict

import rio

from .. import components as comps

__all__ = [
    "InteractiveExample",
    "ColumnExample",
    "RowExample",
    "StackExample",
    "ButtonExample",
]


class InteractiveExample(rio.Component, ABC):
    @abstractmethod
    def build_result_view(self) -> rio.Component:
        ...

    @abstractmethod
    def build_controls(self) -> Dict[str, rio.Component]:
        ...

    def build(self) -> rio.Component:
        # Prepare the result view
        result_view = rio.Container(
            self.build_result_view(),
            width="grow",
            align_x=0.5,
        )

        # If there is no controls, that's it
        if not self.build_controls():
            return result_view

        # Prepare the controls
        control_sections = []

        for name, control in self.build_controls().items():
            control_sections.append(
                rio.Column(
                    rio.Text(name, style="heading3"),
                    control,
                    spacing=0.7,
                )
            )

        # Combine everything
        return rio.Row(
            result_view,
            rio.Card(
                rio.Column(
                    *control_sections,
                    width=12,
                    spacing=1.5,
                    align_y=0,
                ),
                elevate_on_hover=True,
                colorize_on_hover=True,
                width=14,
                align_y=0,
            ),
            spacing=2,
            width="grow",
        )


class ColumnExample(InteractiveExample):
    spacing: float = 0

    def build_result_view(self) -> rio.Component:
        return rio.Column(
            comps.SampleA(),
            comps.SampleB(),
            comps.SampleC(),
            spacing=ColumnExample.spacing,
            align_x=0.5,
        )

    def build_controls(self) -> Dict[str, rio.Component]:
        return {
            "Spacing": rio.Slider(
                min=0,
                max=3,
                value=ColumnExample.spacing,
            ),
        }


class RowExample(InteractiveExample):
    spacing: float = 0

    def build_result_view(self) -> rio.Component:
        return rio.Row(
            comps.SampleA(),
            comps.SampleB(),
            comps.SampleC(),
            spacing=RowExample.spacing,
            align_y=0.5,
        )

    def build_controls(self) -> Dict[str, rio.Component]:
        return {
            "Spacing": rio.Slider(
                min=0,
                max=3,
                value=RowExample.spacing,
            ),
        }


class StackExample(InteractiveExample):
    def build_result_view(self) -> rio.Component:
        return rio.Stack(
            comps.SampleA(
                align_x=0,
                align_y=0,
            ),
            comps.SampleB(
                align_x=0,
                align_y=0,
            ),
            comps.SampleC(
                align_x=0,
                align_y=0,
            ),
            align_x=0.5,
            align_y=0.5,
        )

    def build_controls(self) -> Dict[str, rio.Component]:
        return {}


class ButtonExample(InteractiveExample):
    show_icon: bool = True
    colorset: Literal[
        "primary", "secondary", "success", "warning", "danger"
    ] = "secondary"

    def build_result_view(self) -> rio.Component:
        icon = "material/bolt:fill" if self.show_icon else None
        spacing = 1

        grid = rio.Grid(
            row_spacing=spacing,
            column_spacing=spacing,
        )

        def add_column(
            shape: Literal["pill", "rounded", "rectangle", "circle"],
            col_ii: int,
        ) -> None:
            grid.add_child(
                rio.Button(
                    "Major",
                    shape=shape,
                    icon=icon,
                    color=self.colorset,
                ),
                0,
                col_ii,
            )

            grid.add_child(
                rio.Button(
                    "Minor",
                    shape=shape,
                    icon=icon,
                    color=self.colorset,
                    style="minor",
                ),
                1,
                col_ii,
            )

            grid.add_child(
                rio.Button(
                    "Loading",
                    shape=shape,
                    icon=icon,
                    color=self.colorset,
                    is_loading=True,
                ),
                2,
                col_ii,
            )

            grid.add_child(
                rio.Button(
                    "Insensitive",
                    shape=shape,
                    icon=icon,
                    color=self.colorset,
                    is_sensitive=False,
                ),
                3,
                col_ii,
            )

        add_column("pill", 0)
        add_column("rounded", 1)
        add_column("rectangle", 2)

        # Circular buttons are huge. Add fewer of them.
        grid.add_child(
            rio.Column(
                rio.Button(
                    "Major",
                    shape="circle",
                    color=self.colorset,
                    width=4,
                    height=4,
                ),
                rio.Spacer(),
                rio.Button(
                    "Minor",
                    style="minor",
                    shape="circle",
                    color=self.colorset,
                    width=4,
                    height=4,
                ),
                rio.Spacer(),
                rio.Button(
                    "Loading",
                    shape="circle",
                    color=self.colorset,
                    is_loading=True,
                    width=4,
                    height=4,
                ),
                spacing=spacing * 0.5,  # Account for the spacers
            ),
            0,
            3,
            height=4,
        )

        return grid

    def build_controls(self) -> Dict[str, rio.Component]:
        return {
            "Show Icon": rio.Switch(is_on=ButtonExample.show_icon),
            "Colorset": rio.Dropdown(
                {
                    "Primary": "primary",
                    "Secondary": "secondary",
                    "Success": "success",
                    "Warning": "warning",
                    "Danger": "danger",
                },
                selected_value=ButtonExample.colorset,
            ),
        }
