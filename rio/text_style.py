from __future__ import annotations

import pathlib
from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import common
from .fills import FillLike
from .self_serializing import SelfSerializing

__all__ = [
    "Font",
    "TextStyle",
]


@dataclass(frozen=True)
class Font(SelfSerializing):
    name: str
    regular: pathlib.Path | bytes
    bold: pathlib.Path | bytes | None = None
    italic: pathlib.Path | bytes | None = None
    bold_italic: pathlib.Path | bytes | None = None

    def _serialize(self, sess: rio.Session) -> str:
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
    font: Font | None = None
    fill: FillLike | None = None
    font_size: float = 1.0
    italic: bool = False
    font_weight: Literal["normal", "bold"] = "normal"
    underlined: bool = False
    all_caps: bool = False

    def replace(
        self,
        *,
        font: Font | None = None,
        fill: FillLike | None = None,
        font_size: float | None = None,
        italic: bool | None = None,
        font_weight: Literal["normal", "bold"] | None = None,
        underlined: bool | None = None,
        all_caps: bool | None = None,
    ) -> TextStyle:
        return type(self)(
            font=self.font if font is None else font,
            fill=self.fill if fill is None else fill,
            font_size=self.font_size if font_size is None else font_size,
            italic=self.italic if italic is None else italic,
            font_weight=self.font_weight if font_weight is None else font_weight,
            underlined=self.underlined if underlined is None else underlined,
            all_caps=self.all_caps if all_caps is None else all_caps,
        )

    def _serialize(self, sess: rio.Session) -> JsonDoc:
        return {
            "fontName": None if self.font is None else self.font._serialize(sess),
            "fill": None if self.fill is None else self.fill._serialize(sess),
            "fontSize": self.font_size,
            "italic": self.italic,
            "fontWeight": self.font_weight,
            "underlined": self.underlined,
            "allCaps": self.all_caps,
        }
