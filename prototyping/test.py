import asyncio
import json
from pathlib import Path
from typing import Any, Callable, Optional

import PIL.Image

import web_gui as wg


class Buttons(wg.Widget):
    counter: int = 0

    def inc(self, event: wg.MouseDownEvent) -> None:
        print("clickedy")
        self.counter += 1

    def dec(self, event: wg.MouseDownEvent) -> None:
        print("clickedy")
        self.counter -= 1

    def build(self) -> wg.Widget:
        return wg.Column(
            [
                wg.MouseEventListener(
                    wg.Text(f"You clicked me {self.counter} time(s)!"),
                    on_mouse_down=self.inc,
                ),
                wg.MouseEventListener(
                    wg.Text(f"------------"),
                    on_mouse_down=self.dec,
                ),
            ]
        )


class LsdWidget(wg.Widget):
    text: str = "Hello, World"

    def more_louder(self) -> None:
        self.text += "!"

    def build(self) -> wg.Widget:
        lsd_fill = wg.LinearGradientFill(
            (wg.Color.RED, 0.0),
            (wg.Color.GREEN, 0.5),
            (wg.Color.BLUE, 1.0),
            angle_degrees=45,
        )

        return wg.Column(
            children=[
                wg.Text("Foo", font_weight="bold"),
                wg.Rectangle(fill=wg.Color.BLUE),
                wg.Row(
                    children=[
                        wg.Rectangle(fill=wg.Color.RED),
                        wg.Rectangle(fill=wg.Color.GREY),
                    ],
                ),
                wg.Stack(
                    children=[
                        wg.Text("Bar"),
                        wg.Text("Baz"),
                        wg.Rectangle(fill=wg.Color.GREEN),
                    ]
                ),
                wg.Rectangle(fill=lsd_fill),
                Buttons(),
                wg.Button(
                    text=self.text,
                    on_press=self.more_louder,
                ),
                wg.TextInput(
                    text=__class__.text,
                    placeholder="Type here!",
                ),
            ]
        )


class LoginWidget(wg.Widget):
    username: str
    password: str

    session_token: str = ""

    async def login(self) -> None:
        self.session_token = "..."

    def build(self) -> wg.Widget:
        return wg.Column(
            children=[
                wg.TextInput(text=LoginWidget.username),
                wg.TextInput(text=LoginWidget.password),
                wg.Button(
                    "Login",
                    on_press=self.login,
                ),
            ],
        )


def main():
    app = wg.App(
        "Super Dynamic Website!",
        LsdWidget,
        icon=PIL.Image.open("./prototyping/icon.png"),
    )
    app.run(quiet=False)


if __name__ == "__main__":
    # asyncio.run(main())
    main()
