from pathlib import Path

import numpy as np

import rio


class OldSwitchPanel(rio.Component):
    title: str
    child: rio.Component
    is_visible: bool = True

    async def _on_change_switch(self, event: rio.SwitchChangeEvent) -> None:
        self.is_visible = event.is_on
        print(f"CHANGED: {event.is_on}")
        await self.force_refresh()

    def build(self) -> rio.Component:
        children: list[rio.Component] = [
            rio.Switch(
                OldSwitchPanel.is_visible,
                on_change=self._on_change_switch,
            ),
        ]

        if self.is_visible:
            children.append(self.child)

        return rio.Row(
            *children,
            spacing=1,
            align_x=0.5,
        )


class NewSwitchPanel(rio.Component):
    title: str
    child: rio.Component
    is_visible: bool = False

    def build(self) -> rio.Component:
        return rio.Column(
            rio.Row(
                rio.Text(self.title, align_x=0, style="heading2"),
                rio.Switch(NewSwitchPanel.is_visible),
                spacing=1,
                align_x=0,
            ),
            rio.Revealer(
                None,
                self.child,
                is_open=self.is_visible,
            ),
        )


class RootComponent(rio.Component):
    def build(self) -> rio.Component:
        return OldSwitchPanel(
            "foo",
            rio.Text("foo"),
        )
        return rio.Drawer(
            anchor=rio.Column(
                rio.Button("fooo"),
                rio.Switch(width=10, height=10),
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
            content=rio.Spacer(
                width=10,
            ),
            side="left",
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
