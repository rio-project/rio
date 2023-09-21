from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from pathlib import Path
from typing import *  # type: ignore

from typing_extensions import Self
from uniserde import JsonDoc

from . import self_serializing, session
from .color import Color
from .common import URL

__all__ = [
    "Font",
    "TextStyle",
]


@dataclass(frozen=True)
class Font(self_serializing.SelfSerializing):
    name: str
    location: Union[Path, URL]

    def _serialize(self, sess: session.Session) -> str:
        sess._register_font(self.name, self.location)
        return self.name


@dataclass(frozen=True)
class TextStyle(self_serializing.SelfSerializing):
    _: KW_ONLY
    font: Union[str, Font] = "Roboto"
    font_color: Color = Color.BLACK
    font_size: float = 1.0
    italic: bool = False
    font_weight: Literal["normal", "bold"] = "normal"
    underlined: bool = False
    all_caps: bool = False

    def replace(
        self,
        *,
        font: Union[str, Font, None] = None,
        font_color: Optional[Color] = None,
        font_size: Optional[float] = None,
        italic: Optional[bool] = None,
        font_weight: Optional[Literal["normal", "bold"]] = None,
        underlined: Optional[bool] = None,
        all_caps: Optional[bool] = None,
    ) -> Self:
        return TextStyle(
            font=self.font if font is None else font,
            font_color=self.font_color if font_color is None else font_color,
            font_size=self.font_size if font_size is None else font_size,
            italic=self.italic if italic is None else italic,
            font_weight=self.font_weight if font_weight is None else font_weight,
            underlined=self.underlined if underlined is None else underlined,
            all_caps=self.all_caps if all_caps is None else all_caps,
        )

    def _serialize(self, sess: session.Session) -> JsonDoc:
        if isinstance(self.font, str):
            font_name = self.font
        else:
            font_name = self.font.name

        return {
            "fontName": font_name,
            "fontColor": self.font_color.rgba,
            "fontSize": self.font_size,
            "italic": self.italic,
            "fontWeight": self.font_weight,
            "underlined": self.underlined,
            "allCaps": self.all_caps,
        }
