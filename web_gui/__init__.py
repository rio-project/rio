import dataclasses
import typing
from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass
from typing import (
    Dict,
    Generic,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
    Callable,
)

from typing_extensions import Self, dataclass_transform

from .common import Jsonable
from .styling import *

T = TypeVar("T")


_unique_id_counter = -1


def _make_unique_id() -> int:
    global _unique_id_counter
    _unique_id_counter += 1
    return _unique_id_counter


@dataclass_transform()
class Widget(ABC):
    _dirty: bool = False

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        dataclasses.dataclass(cls)

        for attr in vars(cls).get("__annotations__", ()):
            setattr(cls, attr, StateProperty(attr))

    @property
    def _id(self) -> int:
        try:
            return vars(self)["_id"]
        except KeyError:
            _id = _make_unique_id()
            vars(self)["_id"] = _id
            return _id

    @abstractmethod
    def build(self) -> "Widget":
        raise NotImplementedError

    def _serialize(self) -> Dict[str, Jsonable]:
        return self.build()._serialize()

    def _serialize_state(self) -> Dict[str, Jsonable]:
        result = {}

        for name, typ in typing.get_type_hints(self.__class__).items():
            # Skip built-in values
            if name in ("_dirty",):
                continue

            # Serialize anything with values useful for the client
            if typ is bool or typ is int or typ is float or typ is str:
                # TODO: Optional values? Literal? Tuples?
                value = getattr(self, name)
                result[name] = value

        return result

    def _map_direct_children(self, callback: Callable[["Widget"], "Widget"]):
        for name, typ in typing.get_type_hints(self.__class__).items():
            origin, args = typing.get_origin(typ), typing.get_args(typ)

            # Remap directly contained widgets
            if origin is Widget:
                child = getattr(self, name)
                setattr(self, name, callback(child))

            # Iterate over lists of widgets, remapping their values
            elif origin is list and args[0] is Widget:
                children = getattr(self, name)
                setattr(self, name, [callback(child) for child in children])

            # TODO: What about other containers


class StateProperty(Generic[T]):
    def __init__(self, name: str):
        self.name = name

    @overload
    def __get__(self, instance: Widget, owner: Optional[type] = None) -> T:
        ...

    @overload
    def __get__(self, instance: None, owner: Optional[type] = None) -> Self:
        ...

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


class FundamentalWidget(Widget):
    def build(self) -> "Widget":
        return self


@dataclass
class Text(FundamentalWidget):
    text: str
    _: KW_ONLY
    multiline: bool = False
    font: Optional[str] = None

    def _serialize(self) -> Dict[str, Jsonable]:
        return {
            "id": self._id,
            "type": "text",
        }


@dataclass
class Row(FundamentalWidget):
    children: List[Widget]

    def _serialize(self) -> Dict[str, Jsonable]:
        return {
            "id": self._id,
            "type": "row",
            "children": [child._serialize() for child in self.children],
        }


@dataclass
class Column(FundamentalWidget):
    children: List[Widget]

    def _serialize(self) -> Dict[str, Jsonable]:
        return {
            "id": self._id,
            "type": "column",
            "children": [child._serialize() for child in self.children],
        }


@dataclass
class Rectangle(FundamentalWidget):
    fill: FillLike
    _: KW_ONLY
    corner_radius: Tuple[float, float, float, float] = (0, 0, 0, 0)

    def _serialize(self) -> Dict[str, Jsonable]:
        return {
            "id": self._id,
            "type": "rectangle",
        }


@dataclass
class Stack(FundamentalWidget):
    children: List[Widget]

    def _serialize(self) -> Dict[str, Jsonable]:
        return {
            "id": self._id,
            "type": "stack",
            "children": [child._serialize() for child in self.children],
        }


@dataclass
class Margin(FundamentalWidget):
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

    def _serialize(self) -> Dict[str, Jsonable]:
        return {
            "id": self._id,
            "type": "margin",
            "child": self.child._serialize(),
        }


@dataclass
class Align(FundamentalWidget):
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

    def _serialize(self) -> Dict[str, Jsonable]:
        return {
            "id": str(self._id),
            "type": "align",
            "child": self.child._serialize(),
        }
