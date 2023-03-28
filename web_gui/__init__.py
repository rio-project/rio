from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Union, Optional, TypeVar, Generic, Self, dataclass_transform, overload
import dataclasses
import html
from .styling import *


T = TypeVar('T')


@dataclass_transform()
class Widget(ABC):
    _dirty: bool = False

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        dataclasses.dataclass(cls)

        for attr in vars(cls).get('__annotations__', ()):
            setattr(cls, attr, StateProperty(attr))

    @abstractmethod
    def _as_html(self) -> Iterable[str]:
        raise NotImplementedError()


class StateProperty(Generic[T]):
    def __init__(self, name: str):
        self.name = name

    @overload
    def __get__(self, instance: Widget, owner: Optional[type] = None) -> T: ...
    
    @overload
    def __get__(self, instance: None, owner: Optional[type] = None) -> Self: ...
    
    def __get__(
        self,
        instance: Optional[Widget],
        owner: Optional[type] = None,
    ) -> Union[T, Self]:
        if instance is None:
            return self

        return vars(instance)[self.name]
    
    def __set__(self, instance: Widget, value: T) -> None:
        vars(instance)[self.name] = value
        instance._dirty = True


class Text(Widget):
    text: str
    _: dataclasses.KW_ONLY
    multiline: bool = False

    def _as_html(self) -> Iterable[str]:
        multiline_str = "" if self.multiline else ' style="white-space: nowrap;"'
        yield f"<span{multiline_str}>{html.escape(self.text)}</span>"


class Row(Widget):
    children: Tuple[Widget]

    def __init__(self, *children: Widget):
        super().__init__()
        self.children = children

    def _as_html(self) -> Iterable[str]:
        yield '<div style="width: 100%; height: 100%; display: flex;">'

        for widget in self.children:
            yield from widget._as_html()

        yield "</div>"


class Column(Widget):
    children: Tuple[Widget]

    def __init__(self, *children: Widget):
        super().__init__()
        self.children = children

    def _as_html(self) -> Iterable[str]:
        yield '<div style="width: 100%; height: 100%; display: flex; flex-direction: column;">'

        for widget in self.children:
            yield from widget._as_html()

        yield "</div>"


class Rectangle(Widget):
    color: Color
    _corner_radius: Tuple[float, float, float, float]

    def __init__(
        self,
        *,
        color: Color = Color.GREY,
        corner_radius: float = 0.0,
    ):
        super().__init__()
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

    def _as_html(self) -> Iterable[str]:
        border_radius_str = " ".join(f"{radius}em" for radius in self.corner_radius)
        yield f'<div style="width: 100%; height: 100%; background: {self.color._as_css()}; border-radius: {border_radius_str};"></div>'


class Stack(Widget):
    children: Tuple[Widget]

    def __init__(self, *children: Widget):
        super().__init__()
        self.children = children

    def _as_html(self) -> Iterable[str]:
        yield '<div style="position: relative; width: 100%; height: 100%;">'

        for widget in self.children:
            yield '<div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">'
            yield from widget._as_html()
            yield "</div>"

        yield "</div>"


class Margin(Widget):
    child: Widget
    margin_left: float
    margin_top: float
    margin_right: float
    margin_bottom: float

    def __init__(
        self,
        child: Widget,
        *,
        margin: float = 0,
        margin_horizontal: float = 0,
        margin_vertical: float = 0,
        margin_left: float = 0,
        margin_top: float = 0,
        margin_right: float = 0,
        margin_bottom: float = 0,
    ):
        super().__init__()

        self.child = child

        if margin != 0:
            self.margin_left = margin
            self.margin_top = margin
            self.margin_right = margin
            self.margin_bottom = margin

        elif margin_horizontal != 0:
            self.margin_left = margin_horizontal
            self.margin_top = 0
            self.margin_right = margin_horizontal
            self.margin_bottom = 0

        elif margin_vertical != 0:
            self.margin_left = 0
            self.margin_top = margin_vertical
            self.margin_right = 0
            self.margin_bottom = margin_vertical

        else:
            self.margin_left = margin_left
            self.margin_top = margin_top
            self.margin_right = margin_right
            self.margin_bottom = margin_bottom

    def _as_html(self) -> Iterable[str]:
        yield f'<div style="margin: {self.margin_top}em {self.margin_right}em {self.margin_bottom}em {self.margin_left}em;">'
        yield from self.child._as_html()
        yield "</div>"


class Align(Widget):
    child: Widget
    align_x: Optional[float]
    align_y: Optional[float]

    def __init__(
        self,
        child: Widget,
        *,
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        super().__init__()
        self.child = child
        self.align_x = align_x
        self.align_y = align_y

    @classmethod
    def top(cls, child: Widget):
        return cls(child, align_y=0)

    @classmethod
    def bottom(cls, child: Widget):
        return cls(child, align_y=1)

    @classmethod
    def left(cls, child: Widget):
        return cls(child, align_x=0)

    @classmethod
    def right(cls, child: Widget):
        return cls(child, align_x=1)

    @classmethod
    def top_left(cls, child: Widget):
        return cls(child, align_x=0, align_y=0)

    @classmethod
    def top_center(cls, child: Widget):
        return cls(child, align_x=0.5, align_y=0)

    @classmethod
    def top_right(cls, child: Widget):
        return cls(child, align_x=1, align_y=0)

    @classmethod
    def center_left(cls, child: Widget):
        return cls(child, align_x=0, align_y=0.5)

    @classmethod
    def center(cls, child: Widget):
        return cls(child, align_x=0.5, align_y=0.5)

    @classmethod
    def center_right(cls, child: Widget):
        return cls(child, align_x=1, align_y=0.5)

    @classmethod
    def bottom_left(cls, child: Widget):
        return cls(child, align_x=0, align_y=1)

    @classmethod
    def bottom_center(cls, child: Widget):
        return cls(child, align_x=0.5, align_y=1)

    @classmethod
    def bottom_right(cls, child: Widget):
        return cls(child, align_x=1, align_y=1)

    def _as_html(self) -> Iterable[str]:
        style_props = ""

        if self.align_x is not None:
            style_props += f"justify-content: {self.align_x*100}%;"

        if self.align_y is not None:
            style_props += f"align-items: {self.align_y*100}%;"

        yield f'<div style="width: 100%; height: 100%; display: flex; {style_props}">'
        yield from self.child._as_html()
        yield "</div>"
