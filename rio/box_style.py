from __future__ import annotations

from dataclasses import dataclass
from typing import *  # type: ignore

from typing_extensions import Self
from uniserde import Jsonable

import rio

from . import color, self_serializing, session

__all__ = [
    "BoxStyle",
]


@dataclass(frozen=True)
class BoxStyle(self_serializing.SelfSerializing):
    fill: rio.Fill
    stroke_color: rio.Color
    stroke_width: float
    corner_radius: Tuple[float, float, float, float]
    shadow_color: rio.Color
    shadow_radius: float
    shadow_offset_x: float
    shadow_offset_y: float

    def __init__(
        self,
        *,
        fill: rio.FillLike,
        stroke_color: rio.Color = color.Color.BLACK,
        stroke_width: float = 0.0,
        corner_radius: Union[float, Tuple[float, float, float, float]] = 0.0,
        shadow_color: rio.Color = color.Color.BLACK,
        shadow_radius: float = 0.0,
        shadow_offset_x: float = 0.0,
        shadow_offset_y: float = 0.0,
    ):
        fill = rio.Fill._try_from(fill)

        if isinstance(corner_radius, (int, float)):
            corner_radius = (
                corner_radius,
                corner_radius,
                corner_radius,
                corner_radius,
            )

        vars(self).update(
            fill=fill,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            corner_radius=corner_radius,
            shadow_color=shadow_color,
            shadow_radius=shadow_radius,
            shadow_offset_x=shadow_offset_x,
            shadow_offset_y=shadow_offset_y,
        )

    def replace(
        self,
        *,
        fill: Optional[rio.FillLike] = None,
        stroke_color: Optional[rio.Color] = None,
        stroke_width: Optional[float] = None,
        corner_radius: Optional[Union[float, Tuple[float, float, float, float]]] = None,
        shadow_color: Optional[rio.Color] = None,
        shadow_radius: Optional[float] = None,
        shadow_offset_x: Optional[float] = None,
        shadow_offset_y: Optional[float] = None,
    ) -> Self:
        if fill is not None:
            fill = rio.Fill._try_from(fill)

        if isinstance(corner_radius, (int, float)):
            corner_radius = (
                corner_radius,
                corner_radius,
                corner_radius,
                corner_radius,
            )

        return BoxStyle(
            fill=self.fill if fill is None else fill,
            # Stroke rio.Color
            stroke_color=self.stroke_color if stroke_color is None else stroke_color,
            # Stroke Width
            stroke_width=self.stroke_width if stroke_width is None else stroke_width,
            # Corner Radius
            corner_radius=self.corner_radius
            if corner_radius is None
            else corner_radius,
            # shadow
            shadow_color=self.shadow_color if shadow_color is None else shadow_color,
            shadow_radius=self.shadow_radius
            if shadow_radius is None
            else shadow_radius,
            shadow_offset_x=self.shadow_offset_x
            if shadow_offset_x is None
            else shadow_offset_x,
            shadow_offset_y=self.shadow_offset_y
            if shadow_offset_y is None
            else shadow_offset_y,
        )

    def _serialize(self, sess: session.Session) -> Jsonable:
        return {
            "fill": self.fill._serialize(sess),
            "strokeColor": self.stroke_color.rgba,
            "strokeWidth": self.stroke_width,
            "cornerRadius": self.corner_radius,
            "shadowColor": self.shadow_color.rgba,
            "shadowRadius": self.shadow_radius,
            "shadowOffset": (self.shadow_offset_x, self.shadow_offset_y),
        }
