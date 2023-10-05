from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Iterable, Literal, Tuple, Union

from typing_extensions import TypeAlias
from uniserde import Jsonable

import rio

from . import assets, self_serializing, session
from .color import Color
from .common import ImageLike

__all__ = [
    "Fill",
    "FillLike",
    "ImageFill",
    "LinearGradientFill",
    "SolidFill",
]


class Fill(self_serializing.SelfSerializing, ABC):
    @staticmethod
    def _try_from(value: FillLike) -> "Fill":
        if isinstance(value, Fill):
            return value

        if isinstance(value, Color):
            return SolidFill(value)

        raise TypeError(f"Expected Fill or Color, got {type(value)}")


@dataclass(frozen=True, eq=True)
class SolidFill(Fill):
    color: Color

    def _serialize(self, sess: session.Session) -> Jsonable:
        return {
            "type": "solid",
            "color": self.color.rgba,
        }


@dataclass(frozen=True, eq=True)
class LinearGradientFill(Fill):
    stops: Tuple[Tuple[Color, float], ...]
    angle_degrees: float = 0.0

    def __init__(
        self,
        *stops: Tuple[Color, float],
        angle_degrees: float = 0.0,
    ):
        # Make sure there's at least one stop
        if not stops:
            raise ValueError("Gradients must have at least 1 stop")

        # Sort and store the stops
        vars(self).update(
            stops=tuple(sorted(stops, key=lambda x: x[1])),
            angle_degrees=angle_degrees,
        )

    def _as_css_background(self, sess: rio.Session) -> str:
        # Special case: Just one color
        if len(self.stops) == 1:
            return f"#{self.stops[0][0].hex}"

        # Proper gradient
        stop_strings = []

        for stop in self.stops:
            color = stop[0]
            position = stop[1]
            stop_strings.append(f"#{color.hex} {position * 100}%")

        return (
            f"linear-gradient({90 - self.angle_degrees}deg, {', '.join(stop_strings)})"
        )

    def _serialize(self, sess: session.Session) -> Jsonable:
        return {
            "type": "linearGradient",
            "stops": [(color.rgba, position) for color, position in self.stops],
            "angleDegrees": self.angle_degrees,
        }


class ImageFill(Fill):
    def __init__(
        self,
        image: ImageLike,
        *,
        fill_mode: Literal["fit", "stretch", "tile", "zoom"] = "fit",
    ):
        self._image_asset = assets.Asset.from_image(image)
        self._fill_mode = fill_mode

    def _serialize(self, sess: session.Session) -> Jsonable:
        return {
            "type": "image",
            "fillMode": self._fill_mode,
            "imageUrl": self._image_asset._serialize(sess),
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageFill):
            return NotImplemented

        return (
            self._image_asset == other._image_asset
            and self._fill_mode == other._fill_mode
        )

    def __hash__(self) -> int:
        return hash((self._image_asset, self._fill_mode))

    def _as_css_background(self, sess: rio.Session) -> str:
        # Fetch the escaped URL. That way it cannot interfere with the CSS syntax
        self._image_asset._serialize(sess)
        image_url = str(self._image_asset.url)
        css_url = f"url('{image_url}')"

        if self._fill_mode == "fit":
            return f"{css_url} center/contain no-repeat"
        elif self._fill_mode == "stretch":
            return f"{css_url} top left / 100% 100%"
        elif self._fill_mode == "tile":
            return f"{css_url} left top repeat"
        elif self._fill_mode == "zoom":
            return f"{css_url} center/cover no-repeat"
        else:
            # Invalid fill mode
            raise Exception(f"Invalid fill mode for image fill: {self._fill_mode}")


FillLike: TypeAlias = Union[Fill, Color]
