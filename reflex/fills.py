from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Union, Iterable, Tuple, Literal

from uniserde import Jsonable

from . import app_server, self_serializing
from .assets import Asset
from .color import Color
from .common import ImageLike

__all__ = [
    "Fill",
    "FillLike",
    "ImageFill",
    "LinearGradientFill",
    "SolidFill",
]


FillLike = Union["Fill", "Color"]


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

    def _serialize(self, server: app_server.AppServer) -> Jsonable:
        return {
            "type": "solid",
            "color": self.color.rgba,
        }


@dataclass(frozen=True, eq=True)
class LinearGradientFill(Fill):
    stops: Iterable[Tuple[Color, float]]
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

    def _serialize(self, server: app_server.AppServer) -> Jsonable:
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
        self._image_asset = Asset.from_image(image)
        self._fill_mode = fill_mode

    def _serialize(self, server: app_server.AppServer) -> Jsonable:
        return {
            "type": "image",
            "fillMode": self._fill_mode,
            "imageUrl": self._image_asset._serialize(server),
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageFill):
            return NotImplemented

        return (
            self._image_asset == other._image_asset and
            self._fill_mode == other._fill_mode
        )

    def __hash__(self) -> int:
        return hash((self._image_asset, self._fill_mode))
