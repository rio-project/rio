from dataclasses import KW_ONLY, dataclass
from typing import Literal, Optional, Tuple, Union

from typing_extensions import Self

import reflex as rx

__all__ = [
    "MarkdownStyle",
]


@dataclass(frozen=True)
class MarkdownStyle:
    # Headers
    header_1_style: rx.TextStyle = rx.TextStyle(
        font_size=1.5,
        font_color=rx.Color.BLACK,
    )
    header_2_style: rx.TextStyle = header_1_style.replace(
        font_size=1.35,
    )
    header_3_style: rx.TextStyle = header_1_style.replace(
        font_size=1.25,
    )
    header_4_style: rx.TextStyle = header_1_style.replace(
        font_size=1.15,
        font_weight="bold",
    )
    header_5_style: rx.TextStyle = header_1_style.replace(
        font_size=1.05,
        font_weight="bold",
    )
    header_6_style: rx.TextStyle = header_1_style.replace(
        font_size=1.0,
        font_weight="bold",
    )

    text_body_style: rx.TextStyle = rx.TextStyle()

    hyperlink_style: rx.TextStyle = rx.TextStyle(
        font_color=rx.Color.BLUE,
    )

    def replace(
        self,
        *,
        header_1_style: Optional[rx.TextStyle] = None,
        header_2_style: Optional[rx.TextStyle] = None,
        header_3_style: Optional[rx.TextStyle] = None,
        header_4_style: Optional[rx.TextStyle] = None,
        header_5_style: Optional[rx.TextStyle] = None,
        header_6_style: Optional[rx.TextStyle] = None,
        text_body_style: Optional[rx.TextStyle] = None,
        hyperlink_style: Optional[rx.TextStyle] = None,
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
