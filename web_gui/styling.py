import abc
from typing import Iterable, Tuple, List, Union, Literal


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

    def _as_css(self) -> str:
        return f"rgba({self.red*255}, {self.green*255}, {self.blue*255}, {self.alpha})"

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


class Fill(abc.ABC):
    @abc.abstractmethod
    def _as_css(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _try_from(value: FillLike) -> "Fill":
        if isinstance(value, Fill):
            return value

        if isinstance(value, Color):
            return SolidFill(value)

        raise TypeError(f"Expected Fill or Color, got {type(value)}")


class SolidFill(Fill):
    color: Color

    def __init__(self, color: Color):
        self.color = color

    def _as_css(self) -> str:
        return self.color._as_css()


class LinearGradientFill(Fill):
    def __init__(self, stops: Iterable[Tuple[Color, float]]):
        # Sort and store the stops
        self.stops = tuple(sorted(stops, key=lambda x: x[1]))

        # Make sure there's at least one stop
        if not self.stops:
            raise ValueError("Gradients must have at least 1 stop")

    def _as_css(self) -> str:
        # Special case: solid color
        if len(self.stops) == 1:
            return self.stops[0][0]._as_css()

        # Otherwise build the CSS gradient
        stop_strings = [
            f"{color._as_css()} {position * 100}%" for color, position in self.stops
        ]

        # TODO: What does CSS do if the first / last stop isn't at 0 / 1? Should
        # additional stops be added to make sure they behave as expected?

        return f"linear-gradient({', '.join(stop_strings)})"
