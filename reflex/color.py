import colorsys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import *  # type: ignore

__all__ = [
    "Color",
]


class Color:
    _red: float
    _green: float
    _blue: float
    _opacity: float

    def __init__(self):
        raise RuntimeError(
            "Don't call `Color` directly. Use `from_rgb()` and related methods instead."
        )

    @classmethod
    def from_rgb(
        cls,
        red: float = 1.0,
        green: float = 1.0,
        blue: float = 1.0,
        opacity: float = 1.0,
        *,
        gamma: Union[float, Literal["linear", "srgb"]] = 1.0,
    ) -> "Color":
        if gamma == "linear":
            gamma = 1.0
        elif gamma == "srgb":
            gamma = 2.2

        if red < 0.0 or red > 1.0:
            raise ValueError("`red` must be between 0.0 and 1.0")

        if green < 0.0 or green > 1.0:
            raise ValueError("`green` must be between 0.0 and 1.0")

        if blue < 0.0 or blue > 1.0:
            raise ValueError("`blue` must be between 0.0 and 1.0")

        if opacity < 0.0 or opacity > 1.0:
            raise ValueError("`opacity` must be between 0.0 and 1.0")

        if gamma < 0.0:
            raise ValueError("`gamma` must be positive")

        self = object.__new__(cls)

        self._red = red**gamma
        self._green = green**gamma
        self._blue = blue**gamma
        self._opacity = opacity

        return self

    @classmethod
    def from_hex(cls, hex_color: str) -> "Color":
        # Drop the leading `#` if present
        hex_color = hex_color.removeprefix("#")

        # Make sure the string is the correct length
        if len(hex_color) not in (6, 8):
            raise ValueError("The hex string must be 6 or 8 characters long")

        # Parse it
        return cls.from_rgb(
            red=int(hex_color[0:2], 16) / 255,
            green=int(hex_color[2:4], 16) / 255,
            blue=int(hex_color[4:6], 16) / 255,
            opacity=int(hex_color[6:8], 16) / 255 if len(hex_color) == 8 else 1.0,
        )

    @classmethod
    def from_hsv(
        cls,
        hue: float,
        saturation: float,
        value: float,
        opacity: float = 1.0,
    ) -> "Color":
        if hue < 0.0 or hue > 1.0:
            raise ValueError("`hue` must be between 0.0 and 1.0")

        if saturation < 0.0 or saturation > 1.0:
            raise ValueError("`saturation` must be between 0.0 and 1.0")

        if value < 0.0 or value > 1.0:
            raise ValueError("`value` must be between 0.0 and 1.0")

        # Opacity will be checked by `from_rgb`

        return cls.from_rgb(
            *colorsys.hsv_to_rgb(hue, saturation, value),
            opacity=opacity,
        )

    @classmethod
    def from_grey(cls, grey: float, opacity: float = 1.0) -> "Color":
        """
        Create a grey color with the given intensity. A `grey` value of 0.0
        corresponds to black, and 1.0 to white.
        """
        if grey < 0.0 or grey > 1.0:
            raise ValueError("`grey` must be between 0.0 and 1.0")

        # Opacity will be checked by `from_rgb`

        return cls.from_rgb(grey, grey, grey, opacity)

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
    def opacity(self) -> float:
        return self._opacity

    @property
    def rgb(self) -> Tuple[float, float, float]:
        return (self._red, self._green, self._blue)

    @property
    def rgba(self) -> Tuple[float, float, float, float]:
        return (self._red, self._green, self._blue, self._opacity)

    @property
    def hsv(self) -> Tuple[float, float, float]:
        return colorsys.rgb_to_hsv(self._red, self._green, self._blue)

    @property
    def hue(self) -> float:
        return self.hsv[0]

    @property
    def saturation(self) -> float:
        return self.hsv[1]

    @property
    def value(self) -> float:
        return self.hsv[2]

    @property
    def hex(self) -> str:
        red_hex = f"{int(round(self.red*255)):02x}"
        green_hex = f"{int(round(self.green*255)):02x}"
        blue_hex = f"{int(round(self.blue*255)):02x}"
        return red_hex + green_hex + blue_hex

    def replace(
        self,
        *,
        red: Optional[float] = None,
        green: Optional[float] = None,
        blue: Optional[float] = None,
        opacity: Optional[float] = None,
    ) -> "Color":
        return Color.from_rgb(
            red=self.red if red is None else red,
            green=self.green if green is None else green,
            blue=self.blue if blue is None else blue,
            opacity=self.opacity if opacity is None else opacity,
        )

    def _map_rgb(self, func: Callable[[float], float]) -> "Color":
        """
        Apply a function to each of the RGB values of this color, and return
        a new `Color` instance with the result. The opacity value is copied
        unchanged.
        """
        return Color.from_rgb(
            func(self.red),
            func(self.green),
            func(self.blue),
            self.opacity,
        )

    def brighter(self, amount: float) -> "Color":
        """
        Return a new `Color` instance that is brighter than this one by the
        given amount. `0` means no change, `1` will turn the color into white.
        Values less than `0` will darken the color instead.

        How exactly the darkening happens isn't defined.
        """
        # The amount may be negative. If that is the case, delegate to `darker`
        if amount <= 0:
            return self.darker(-amount)

        # HSV has an explicit value for brightness, so convert to HSV and bump
        # the value.
        #
        # Brightening by `1` is supposed to yield white, but because this
        # function starts shifting colors to white after they exceed `1.0` an
        # amount of `2` might be needed to actually get white.
        #
        # -> Apply double the amount
        hue, saturation, value = self.hsv
        value += amount * 2

        # Bumping it might put the value above 1.0. Clip it and see by how much
        # 1.0 was overshot
        value_clip = max(min(value, 1.0), 0.0)
        overshoot = value - value_clip

        # If there was an overshoot, reduce the saturation, thus pushing the
        # color towards white
        saturation = max(saturation - overshoot * 1.0, 0.0)

        return Color.from_hsv(hue, saturation, value_clip)

    def darker(self, amount: float) -> "Color":
        """
        Return a new `Color` instance that is darker than this one by the
        given amount. `0` means no change, `1` will turn the color into black.
        Values less than `0` will brighten the color instead.
        """
        # The value may be negative. If that is the case, delegate to `brighter`
        if amount <= 0:
            return self.brighter(-amount)

        return Color._map_rgb(self, lambda x: max(x - amount, 0))

    def contrasting(self, scale: float = 0.5) -> "Color":
        """
        Return a color which is similar to this one, but different enough to be
        legible when used as text on top of this color.

        `scale` controls just how different the color will be. A value of `0`
        will return the same color, a value of `1` will return a color that is
        as contrasting as possible.
        """
        if scale < 0.0 or scale > 1.0:
            raise ValueError("`scale` must be between 0.0 and 1.0")

        hue, saturation, brightness = self.hsv

        if brightness > 0.5:
            brightness = brightness * (1 - scale)
        else:
            brightness = brightness + (1 - brightness) * scale

        # Convert back to linear brightness
        brightness = brightness**2.2

        return Color.from_hsv(hue, saturation, brightness)

    def desaturated(self, amount: float) -> "Color":
        """
        Return a copy of this color with the saturation reduced by the given
        amount. `0` means no change, `1` will turn the color into a shade of
        grey.
        """

        if amount < 0.0 or amount > 1.0:
            raise ValueError("`amount` must be between 0.0 and 1.0")

        hue, saturation, brightness = self.hsv
        saturation = saturation * (1 - amount)

        return Color.from_hsv(hue, saturation, brightness)

    def blend(self, other: "Color", factor: float) -> "Color":
        """
        Return a new `Color` instance that is a blend of this color and the
        given `other` color. `factor` controls how much of the other color is
        used. A value of `0` will return this color, a value of `1` will return
        the other color.

        Values outside of the range `0` to `1` are allowed and will lead to the
        color being extrapolated.
        """
        one_minus_factor = 1 - factor

        return Color.from_rgb(
            red=self.red * one_minus_factor + other.red * factor,
            green=self.green * one_minus_factor + other.green * factor,
            blue=self.blue * one_minus_factor + other.blue * factor,
            opacity=self.opacity * one_minus_factor + other.opacity * factor,
        )

    def as_plotly(self) -> str:
        return f"rgba({int(round(self.red*255))}, {int(round(self.green*255))}, {int(round(self.blue*255))}, {int(round(self.opacity*255))})"

    def __repr__(self) -> str:
        return f"<Color {self.hex}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return NotImplemented

        return self.rgba == other.rgba

    def __hash__(self) -> int:
        return hash(self.rgba)

    # Greys
    BLACK: ClassVar["Color"]
    GREY: ClassVar["Color"]
    WHITE: ClassVar["Color"]

    # Pure colors
    RED: ClassVar["Color"]
    GREEN: ClassVar["Color"]
    BLUE: ClassVar["Color"]

    # CMY
    CYAN: ClassVar["Color"]
    MAGENTA: ClassVar["Color"]
    YELLOW: ClassVar["Color"]

    # Others
    PURPLE: ClassVar["Color"]

    # Special
    TRANSPARENT: ClassVar["Color"]


Color.BLACK = Color.from_rgb(0.0, 0.0, 0.0)
Color.GREY = Color.from_rgb(0.5, 0.5, 0.5)
Color.WHITE = Color.from_rgb(1.0, 1.0, 1.0)

Color.RED = Color.from_rgb(1.0, 0.0, 0.0)
Color.GREEN = Color.from_rgb(0.0, 1.0, 0.0)
Color.BLUE = Color.from_rgb(0.0, 0.0, 1.0)

Color.CYAN = Color.from_rgb(0.0, 1.0, 1.0)
Color.MAGENTA = Color.from_rgb(1.0, 0.0, 1.0)
Color.YELLOW = Color.from_rgb(1.0, 1.0, 0.0)

Color.PURPLE = Color.from_rgb(0.5, 0.0, 0.5)

Color.TRANSPARENT = Color.from_rgb(0.0, 0.0, 0.0, 0.0)
