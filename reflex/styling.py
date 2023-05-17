import enum
from abc import ABC, abstractmethod
from typing import Dict, Iterable, List, Literal, Tuple, Union

from .common import Jsonable

__all__ = [
    "Color",
    "Fill",
    "FillLike",
    "SolidFill",
    "LinearGradientFill",
]


FillLike = Union["Fill", "Color"]


class Color:
    _red: float
    _green: float
    _blue: float
    _alpha: float

    def __init__(self):
        raise RuntimeError(
            "Don't call this constructor directly. Use `from_rgb()` and related methods instead."
        )

    @classmethod
    def from_rgb(
        cls,
        red: float = 1.0,
        green: float = 1.0,
        blue: float = 1.0,
        alpha: float = 1.0,
        *,
        gamma: Union[float, Literal["srgb"]] = 1.0,
    ) -> "Color":
        if gamma == "srgb":
            gamma = 2.2

        self = object.__new__(cls)

        self._red = red**gamma
        self._green = green**gamma
        self._blue = blue**gamma
        self._alpha = alpha

        return self

    @classmethod
    def from_hex(cls, hex_color: str) -> "Color":
        if len(hex_color) not in (6, 8):
            raise ValueError("The hex string must be 6 or 8 characters long")

        return cls.from_rgb(
            red=int(hex_color[0:2], 16) / 255,
            green=int(hex_color[2:4], 16) / 255,
            blue=int(hex_color[4:6], 16) / 255,
            alpha=int(hex_color[6:8], 16) / 255 if len(hex_color) == 8 else 1.0,
            gamma="srgb",
        )

    GREY: "Color"
    BLACK: "Color"
    RED: "Color"
    GREEN: "Color"
    BLUE: "Color"
    WHITE: "Color"

    @property
    def red(self) -> float:
        return self._red

    @property
    def green(self) -> float:
        return self._green

    @property
    def blue(self) -> float:
        return self._blue

    @property
    def alpha(self) -> float:
        return self._alpha

    @property
    def rgb(self) -> Tuple[float, float, float]:
        return (self.red, self.green, self.blue)

    @property
    def rgba(self) -> Tuple[float, float, float, float]:
        return (self.red, self.green, self.blue, self.alpha)

    @property
    def hex(self) -> str:
        raise NotImplementedError("TODO: Untested")
        # TODO: Gamma
        # TODO: Alpha
        return f"{self.red*255:02x}{self.green*255:02x}{self.blue*255:02x}"

    # TODO:
    # - from/to hsv
    # - range checks (allow hdr?)
    # - method for cloning, with optional overrides


Color.BLACK = Color.from_rgb(0.0, 0.0, 0.0)
Color.RED = Color.from_rgb(1.0, 0.0, 0.0)
Color.GREEN = Color.from_rgb(0.0, 1.0, 0.0)
Color.BLUE = Color.from_rgb(0.0, 0.0, 1.0)
Color.WHITE = Color.from_rgb(1.0, 1.0, 1.0)
Color.GREY = Color.from_rgb(0.5, 0.5, 0.5)


class Fill(ABC):
    @staticmethod
    def _try_from(value: FillLike) -> "Fill":
        if isinstance(value, Fill):
            return value

        if isinstance(value, Color):
            return SolidFill(value)

        raise TypeError(f"Expected Fill or Color, got {type(value)}")

    @abstractmethod
    def _serialize(self) -> Dict[str, Jsonable]:
        raise NotImplementedError()


class SolidFill(Fill):
    color: Color

    def __init__(self, color: Color):
        self.color = color

    def _serialize(self) -> Dict[str, Jsonable]:
        return {
            "type": "solid",
            "color": self.color.rgba,
        }


class LinearGradientFill(Fill):
    def __init__(
        self,
        *stops: Tuple[Color, float],
        angle_degrees: float = 0.0,
    ):
        # Sort and store the stops
        self.stops = tuple(sorted(stops, key=lambda x: x[1]))

        # Make sure there's at least one stop
        if not self.stops:
            raise ValueError("Gradients must have at least 1 stop")

        self.angle_degrees = angle_degrees

    def _serialize(self) -> Dict[str, Jsonable]:
        return {
            "type": "linearGradient",
            "stops": [(color.rgba, position) for color, position in self.stops],
            "angleDegrees": self.angle_degrees,
        }
