from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from pathlib import Path
from typing import *  # type: ignore

from typing_extensions import Self
from uniserde import JsonDoc

from . import common, session
from .color import Color
from .fills import FillLike
from .self_serializing import SelfSerializing

__all__ = [
    "Font",
    "TextStyle",
]


@dataclass(frozen=True)
class Font(SelfSerializing):
    name: str
    regular: Union[Path, bytes]
    bold: Union[Path, bytes, None] = None
    italic: Union[Path, bytes, None] = None
    bold_italic: Union[Path, bytes, None] = None

    def _serialize(self, sess: session.Session) -> str:
        sess._register_font(self)
        return self.name


ROBOTO = Font(
    "Roboto",
    regular=common.HOSTED_ASSETS_DIR / "fonts/Roboto/Roboto-Regular.ttf",
    bold=common.HOSTED_ASSETS_DIR / "fonts/Roboto/Roboto-Bold.ttf",
    italic=common.HOSTED_ASSETS_DIR / "fonts/Roboto/Roboto-Italic.ttf",
    bold_italic=common.HOSTED_ASSETS_DIR / "fonts/Roboto/Roboto-BoldItalic.ttf",
)

ROBOTO_MONO = Font(
    "Roboto Mono",
    regular=common.HOSTED_ASSETS_DIR / "fonts/Roboto Mono/RobotoMono-Regular.ttf",
    bold=common.HOSTED_ASSETS_DIR / "fonts/Roboto Mono/RobotoMono-Bold.ttf",
    italic=common.HOSTED_ASSETS_DIR / "fonts/Roboto Mono/RobotoMono-Italic.ttf",
    bold_italic=common.HOSTED_ASSETS_DIR
    / "fonts/Roboto Mono/RobotoMono-BoldItalic.ttf",
)


@dataclass(frozen=True)
class TextStyle(SelfSerializing):
    _: KW_ONLY
    font: Font = ROBOTO
    fill: FillLike = Color.BLACK
    font_size: float = 1.0
    italic: bool = False
    font_weight: Literal["normal", "bold"] = "normal"
    underlined: bool = False
    all_caps: bool = False

    def replace(
        self,
        *,
        font: Optional[Font] = None,
        fill: Optional[FillLike] = None,
        font_size: Optional[float] = None,
        italic: Optional[bool] = None,
        font_weight: Optional[Literal["normal", "bold"]] = None,
        underlined: Optional[bool] = None,
        all_caps: Optional[bool] = None,
    ) -> Self:
        return type(self)(
            font=self.font if font is None else font,
            fill=self.fill if fill is None else fill,
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
            font_name = self.font._serialize(sess)

        return {
            "fontName": font_name,
            "fill": self.fill._serialize(sess),
            "fontSize": self.font_size,
            "italic": self.italic,
            "fontWeight": self.font_weight,
            "underlined": self.underlined,
            "allCaps": self.all_caps,
        }
