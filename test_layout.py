from pathlib import Path

import numpy as np

import rio
import website


class RootComponent(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text(
                "This is a heading",
                style="heading1",
            ),
            rio.ListView(
                rio.HeadingListItem("heeeey"),
                rio.SimpleListItem("Entry 1"),
                rio.SimpleListItem("Entry 2"),
                rio.CustomListItem(
                    rio.Row(rio.Button("Click me!"), rio.Spacer(), rio.Text("bar"))
                ),
                rio.HeadingListItem("heeeey again"),
                rio.SimpleListItem("Entry 3"),
            ),
            align_y=0.2,
        )


app = rio.App(
    build=RootComponent,
    theme=rio.Theme.from_color(
        primary_color=rio.Color.ORANGE,
        light=True,
    ),
)


app.run_as_web_server(
    port=8001,
)
