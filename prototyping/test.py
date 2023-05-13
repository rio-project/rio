import asyncio
import json
from pathlib import Path

import PIL.Image

import web_gui.widgets as widgets
from web_gui import *


class Buttons(Widget):
    counter: int = 0

    def inc(self, event: MouseDownEvent) -> None:
        print("clickedy")
        self.counter += 1

    def dec(self, event: MouseDownEvent) -> None:
        print("clickedy")
        self.counter -= 1

    def build(self) -> Widget:
        return Column(
            [
                MouseEventListener(
                    Text(f"You clicked me {self.counter} time(s)!"),
                    on_mouse_down=self.inc,
                ),
                MouseEventListener(
                    Text(f"------------"),
                    on_mouse_down=self.dec,
                ),
            ]
        )


class LsdWidget(Widget):
    def build(self) -> Widget:
        lsd_fill = LinearGradientFill(
            (Color.RED, 0.0),
            (Color.GREEN, 0.5),
            (Color.BLUE, 1.0),
            angle_degrees=45,
        )

        return Column(
            children=[
                Text("Foo", font_weight="bold"),
                Rectangle(fill=Color.BLUE),
                Row(
                    children=[
                        Rectangle(fill=Color.RED),
                        Rectangle(fill=Color.GREY),
                    ],
                ),
                Stack(
                    children=[
                        Text("Bar"),
                        Text("Baz"),
                        Rectangle(fill=Color.GREEN),
                    ]
                ),
                Rectangle(fill=lsd_fill),
                Buttons(),
            ]
        )


class DiffusionWidget(Widget):
    def build(self) -> Widget:
        return Stack(
            [
                Rectangle(
                    fill=Color.RED,
                    corner_radius=(2.0, 2.0, 2.0, 2.0),
                ),
                Column(
                    children=[
                        Text(
                            "Positive Prompt Example, Lorem Ipsum dolor sit amet",
                            multiline=True,
                        ),
                        Text(
                            "Negative Prompt Example, Lorem Ipsum dolor sit amet",
                            multiline=True,
                        ),
                        Row(
                            children=[
                                Text("Euler A"),
                                Text("20 Steps"),
                            ],
                        ),
                        Text("CFG 7.0"),
                        Text("Tilable"),
                    ],
                ),
            ]
        )


def main():
    app = App(
        "Super Dynamic Website!",
        LsdWidget,
        icon=PIL.Image.open("./prototyping/icon.png"),
    )
    app.run(quiet=False)


if __name__ == "__main__":
    # asyncio.run(main())
    main()
