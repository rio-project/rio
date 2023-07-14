from dataclasses import KW_ONLY, dataclass
from typing import Dict, Literal, Optional

from typing_extensions import Self

from ..common import Jsonable
from .color import Color


@dataclass(frozen=True)
class TextStyle:
    _: KW_ONLY
    font_name: Optional[str] = None
    font_color: Color = Color.BLACK
    font_size: float = 1.0
    italic: bool = False
    font_weight: Literal["normal", "bold"] = "normal"
    underlined: bool = False
    all_caps: bool = False

    def replace(
        self,
        *,
        font_name: Optional[str] = None,
        font_color: Optional[Color] = None,
        font_size: Optional[float] = None,
        italic: Optional[bool] = None,
        font_weight: Optional[Literal["normal", "bold"]] = None,
        underlined: Optional[bool] = None,
        all_caps: Optional[bool] = None,
    ) -> Self:
        return TextStyle(
            font_name=self.font_name if font_name is None else font_name,
            font_color=self.font_color if font_color is None else font_color,
            font_size=self.font_size if font_size is None else font_size,
            italic=self.italic if italic is None else italic,
            font_weight=self.font_weight if font_weight is None else font_weight,
            underlined=self.underlined if underlined is None else underlined,
            all_caps=self.all_caps if all_caps is None else all_caps,
        )

    def _serialize(self) -> Dict[str, Jsonable]:
        return {
            "fontName": self.font_name,
            "fontColor": self.font_color.rgba,
            "fontSize": self.font_size,
            "italic": self.italic,
            "fontWeight": self.font_weight,
            "underlined": self.underlined,
            "allCaps": self.all_caps,
        }
