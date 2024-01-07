from pathlib import Path

import numpy as np

import rio


class RootComponent(rio.Component):
    def build(self) -> rio.Component:
        return rio.Drawer(
            anchor=rio.Column(
                rio.Button("fooo"),
                rio.Switch(width=10, height=10),
                rio.TextInput(
                    "foooo",
                    label="bar",
                    prefix_text="pre",
                    suffix_text="suf",
                ),
                rio.MediaPlayer(
                    Path("/home/jakob/Videos/Miscellaneous/Timelapse (La Palma).mp4"),
                    # Path(
                    #     "/home/jakob/Music/Crypt Of The Necrodancer/01 - Tombtorial (Tutorial).mp3"
                    # ),
                    autoplay=True,
                    muted=True,
                    width="grow",
                    height="grow",
                    background=rio.Color.BLACK,
                ),
            ),
            content=rio.Column(
                rio.TextInput(
                    "foooo",
                    label="bar",
                    prefix_text="pre",
                    suffix_text="suf",
                ),
                width=10,
            ),
            side="left",
            is_open=True,
            is_modal=False,
            margin=3,
        )


app = rio.App(
    # build=rio.AppRoot,
    build=RootComponent,
    theme=rio.Theme.from_color(
        rio.Color.YELLOW,
        light=True,
    ),
)


app.run_as_web_server(
    port=8001,
)
