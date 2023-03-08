import asyncio
import webview
from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Union
import html


class Color:
    r: float
    g: float
    b: float
    a: float

    def __init__(self):
        raise RuntimeError(
            "Don't call this constructor directly. Use `srgb()` and related methods instead."
        )

    @classmethod
    def srgb(cls, r: float, g: float, b: float, a: float = 1.0) -> "Color":
        if not 0 <= r <= 1:
            raise ValueError("r must be between 0 and 1")

        if not 0 <= g <= 1:
            raise ValueError("g must be between 0 and 1")

        if not 0 <= b <= 1:
            raise ValueError("b must be between 0 and 1")

        if not 0 <= a <= 1:
            raise ValueError("a must be between 0 and 1")

        self = cls.__new__(cls)

        self.r = r
        self.g = g
        self.b = b
        self.a = a

        return self

    GREY: "Color"

    def to_css(self) -> str:
        return f"rgba({self.r * 255}, {self.g * 255}, {self.b * 255}, {self.a})"


Color.GREY = Color.srgb(0.5, 0.5, 0.5)


class Widget(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def to_html(self) -> Iterable[str]:
        raise NotImplementedError()


class Label(Widget):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def to_html(self) -> Iterable[str]:
        yield f"<span>{html.escape(self.text)}</span>"


class Row(Widget):
    children: Tuple[Widget]

    def __init__(self, *children: Widget):
        super().__init__()
        self.children = children

    def to_html(self) -> Iterable[str]:
        yield '<div style="display: flex;">'
        for widget in self.children:
            yield from widget.to_html()
        yield "</div>"


class Rectangle(Widget):
    width: float
    height: float
    color: Color
    _corner_radius: Tuple[float, float, float, float]

    def __init__(
        self,
        *,
        width: float = 1,
        height: float = 1,
        color: Color = Color.GREY,
        corner_radius: float = 0.0,
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.color = color
        self.corner_radius = corner_radius

    @property
    def corner_radius(self) -> Tuple[float, float, float, float]:
        return self._corner_radius

    @corner_radius.setter
    def corner_radius(self, value: Union[float, Iterable[float]]):
        if isinstance(value, (int, float)):
            self._corner_radius = (value, value, value, value)
        else:
            value = tuple(value)

            if len(value) != 4:
                raise ValueError(
                    "The corner radius must either be a float or a 4-tuple of floats"
                )

            self._corner_radius = value

    def to_html(self) -> Iterable[str]:
        yield f"<div style='width: {self.width}em; height: {self.height}em; background-color: {self.color.to_css()}; border-radius: {self.corner_radius}em;'></div>"


async def main():
    gui = Row(
        Rectangle(width=3, height=2, color=Color.srgb(1, 0, 0)),
        Rectangle(width=3, height=2, color=Color.srgb(0, 1, 0)),
        Label("Hello, world!"),
    )

    html = "".join(gui.to_html())

    webview.create_window("Hello world", html=html)
    webview.start()


if __name__ == "__main__":
    asyncio.run(main())
