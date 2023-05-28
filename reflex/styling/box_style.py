from typing_extensions import Self
from typing import Optional, Dict, Union, Tuple
from .color import Color
from dataclasses import dataclass
from ..common import Jsonable
from . import fills


@dataclass(frozen=True)
class BoxStyle:
    fill: fills.Fill
    stroke_color: Color
    stroke_width: float
    corner_radius: Tuple[float, float, float, float]

    def __init__(
        self,
        *,
        fill: fills.FillLike,
        stroke_color: Color = Color.BLACK,
        stroke_width: float = 0.0,
        corner_radius: Union[float, Tuple[float, float, float, float]] = 0.0,
    ):
        fill = fills.Fill._try_from(fill)

        if isinstance(corner_radius, (int, float)):
            corner_radius = (
                corner_radius,
                corner_radius,
                corner_radius,
                corner_radius,
            )

        object.__setattr__(self, "fill", fill)
        object.__setattr__(self, "stroke_color", stroke_color)
        object.__setattr__(self, "stroke_width", stroke_width)
        object.__setattr__(self, "corner_radius", corner_radius)

    def replace(
        self,
        *,
        fill: Optional[fills.FillLike] = None,
        stroke_color: Optional[Color] = None,
        stroke_width: Optional[float] = None,
        corner_radius: Optional[Union[float, Tuple[float, float, float, float]]] = None,
    ) -> Self:
        if fill is not None:
            fill = fills.Fill._try_from(fill)

        if isinstance(corner_radius, (int, float)):
            corner_radius = (
                corner_radius,
                corner_radius,
                corner_radius,
                corner_radius,
            )

        return BoxStyle(
            fill=fill if fill is not None else self.fill,
            # Stroke Color
            stroke_color=self.stroke_color if stroke_color is None else stroke_color,
            # Stroke Width
            stroke_width=self.stroke_width if stroke_width is None else stroke_width,
            # Corner Radius
            corner_radius=self.corner_radius
            if corner_radius is None
            else corner_radius,
        )

    def _serialize(self, external_server_url: str) -> Dict[str, Jsonable]:
        return {
            "fill": self.fill._serialize(external_server_url),
            "strokeColor": self.stroke_color.rgba,
            "strokeWidth": self.stroke_width,
            "cornerRadius": self.corner_radius,
        }
