from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from uniserde import JsonDoc

from .. import text_style
from . import component_base

__all__ = [
    "Text",
]


class Text(component_base.FundamentalComponent):
    """
    Displays unformatted text.

    `Text` displays text without any formatting, making it one of the most
    commonly used components in Rio.

    While the text itself is unformatted, you can still control the style of
    the text using the `style` attribute. This allows you to change the font
    size, color, and more.

    Attributes:
        text: The text to display.

        multiline: Whether the text may be split into multiple lines if not
            enough space is available.

        selectable: Whether the text can be selected by the user.

        style: The style of the text. This can either be a `TextStyle` instance,
            or one of the built-in styles: `heading1`, `heading2`, `heading3`,
            or `text`.
    """

    text: str
    multiline: bool
    selectable: bool
    style: Union[
        Literal["heading1", "heading2", "heading3", "text", "dim"],
        text_style.TextStyle,
    ]

    _text_align: float | Literal["justify"]

    def __init__(
        self,
        text: str,
        *,
        multiline: bool = False,
        selectable: bool = False,
        style: Union[
            Literal["heading1", "heading2", "heading3", "text", "dim"],
            text_style.TextStyle,
        ] = "text",
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["natural", "grow"], float] = "natural",
        height: Union[Literal["natural", "grow"], float] = "natural",
        align_x: float | Literal["justify"] = 0.5,
        align_y: Optional[float] = None,
    ):
        if align_x not in (0, 0.5, 1, "justify"):
            raise ValueError(
                f'`align_x` in texts can has to be either 0, 0.5, 1 or "justify", not {align_x}. This is different from other components, because texts align each line individually.'
            )

        super().__init__(
            key=key,
            margin=margin,
            margin_x=margin_x,
            margin_y=margin_y,
            margin_left=margin_left,
            margin_top=margin_top,
            margin_right=margin_right,
            margin_bottom=margin_bottom,
            width=width,
            height=height,
            # Note that align_x is not passed on. The fundamental widget instead
            # sets its text align.
            align_x=None,
            align_y=align_y,
        )

        self.text = text
        self.multiline = multiline
        self.selectable = selectable
        self.style = style
        self._text_align = align_x

    def _custom_serialize(self) -> JsonDoc:
        # Serialization doesn't handle unions. Hence the custom serialization
        # here
        if isinstance(self.style, str):
            style = self.style
        else:
            style = self.style._serialize(self.session)

        return {
            "style": style,
            "text_align": self._text_align,
        }


Text._unique_id = "Text-builtin"
