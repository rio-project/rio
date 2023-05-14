import asyncio
import json
from pathlib import Path
from typing import Any, Callable, Optional

import PIL.Image

import web_gui as wg


class Button(wg.Widget):
    text: str
    on_press: Optional[Callable[[], Any]] = None
    _is_pressed: bool = False

    def _on_mouse_down(self, event: wg.MouseDownEvent) -> None:
        self._is_pressed = True

    def _on_mouse_up(self, event: wg.MouseUpEvent) -> None:
        if self.on_press is None:
            return

        self.on_press()
        self._is_pressed = False

    def build(self) -> wg.Widget:
        return wg.MouseEventListener(
            wg.Stack(
                [
                    wg.Rectangle(wg.Color.RED if self._is_pressed else wg.Color.GREEN),
                    wg.Margin(
                        wg.Text(self.text),
                        margin=0.3,
                    ),
                ]
            ),
            on_mouse_down=self._on_mouse_down,
            on_mouse_up=self._on_mouse_up,
        )


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
                Button(
                    text="Click me!",
                    on_press=lambda: print("Clicked!"),
                ),
            ]
        )


class LsdWidget(wg.Widget):
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
            ]
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
