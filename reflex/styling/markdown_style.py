from dataclasses import KW_ONLY, dataclass
from typing import Literal, Optional, Tuple, Union

from typing_extensions import Self

from .. import theme
from . import text_style


@dataclass(frozen=True)
class MarkdownStyle:
    # Headers
    header_1_style: text_style.TextStyle = text_style.TextStyle(
        font_size=1.5,
        font_color=theme.COLOR_FONT,
    )
    header_2_style: text_style.TextStyle = header_1_style.replace(
        font_size=1.35,
    )
    header_3_style: text_style.TextStyle = header_1_style.replace(
        font_size=1.25,
    )
    header_4_style: text_style.TextStyle = header_1_style.replace(
        font_size=1.15,
        font_weight="bold",
    )
    header_5_style: text_style.TextStyle = header_1_style.replace(
        font_size=1.05,
        font_weight="bold",
    )
    header_6_style: text_style.TextStyle = header_1_style.replace(
        font_size=1.0,
        font_weight="bold",
    )

    text_body_style: text_style.TextStyle = text_style.TextStyle()

    hyperlink_style: text_style.TextStyle = text_style.TextStyle(
        font_color=theme.COLOR_ACCENT,
    )

    def replace(
        self,
        *,
        header_1_style: Optional[text_style.TextStyle] = None,
        header_2_style: Optional[text_style.TextStyle] = None,
        header_3_style: Optional[text_style.TextStyle] = None,
        header_4_style: Optional[text_style.TextStyle] = None,
        header_5_style: Optional[text_style.TextStyle] = None,
        header_6_style: Optional[text_style.TextStyle] = None,
        text_body_style: Optional[text_style.TextStyle] = None,
        hyperlink_style: Optional[text_style.TextStyle] = None,
    ) -> Self:
        return MarkdownStyle(
            header_1_style=self.header_1_style
            if header_1_style is None
            else header_1_style,
            header_2_style=self.header_2_style
            if header_2_style is None
            else header_2_style,
            header_3_style=self.header_3_style
            if header_3_style is None
            else header_3_style,
            header_4_style=self.header_4_style
            if header_4_style is None
            else header_4_style,
            header_5_style=self.header_5_style
            if header_5_style is None
            else header_5_style,
            header_6_style=self.header_6_style
            if header_6_style is None
            else header_6_style,
            text_body_style=self.text_body_style
            if text_body_style is None
            else text_body_style,
            hyperlink_style=self.hyperlink_style
            if hyperlink_style is None
            else hyperlink_style,
        )
