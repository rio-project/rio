from pathlib import Path

import numpy as np

import rio
import website


def make_slideshow_placeholder(variant: int) -> rio.Component:
    colors = [
        rio.Color.RED,
        rio.Color.GREEN,
        rio.Color.BLUE,
        rio.Color.YELLOW,
        rio.Color.PURPLE,
        rio.Color.MAGENTA,
    ]

    return rio.Rectangle(
        child=rio.Text(
            f"Slideshow Page {variant}",
        ),
        style=rio.BoxStyle(
            fill=colors[variant % len(colors)],
        ),
        width="grow",
        height="grow",
    )


class RootComponent(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Row(
                rio.Text("Foo"),
                rio.Text("Bar"),
            ),
        )

        return rio.Row(
            rio.Text("Hello 1!"),
            rio.Text("Hello 2!", width=20),
            rio.Text("Hello 3!", width="grow"),
            rio.TextInput("Hello 3!", align_y=0.5),
            rio.Column(
                rio.Text("Hello 4!"),
                rio.Text("Hello 5!"),
                rio.Revealer(
                    header="Revealer",
                    content=rio.Text(
                        "You found me",
                        height=3,
                    ),
                ),
                rio.Text("Hello 6!"),
                spacing=1,
                align_y=0,
            ),
            rio.Button(
                "foofoo",
                on_press=self.force_refresh,
                align_x=0.5,
                align_y=0.5,
            ),
            spacing=3,
        )


app = rio.App(
    build=RootComponent,
    # build_connection_lost_message=lambda: rio.Text("OMG you forgot about me"),
)


app.run_as_web_server(
    port=8001,
)
