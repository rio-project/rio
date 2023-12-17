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
    _: KW_ONLY
    multiline: bool = False
    selectable: bool = False
    style: Union[
        Literal["heading1", "heading2", "heading3", "text", "dim"],
        text_style.TextStyle,
    ] = "text"

    def _custom_serialize(self) -> JsonDoc:
        # Serialization doesn't handle unions. Hence the custom serialization
        # here
        if isinstance(self.style, str):
            style = self.style
        else:
            style = self.style._serialize(self.session)

        return {
            "style": style,
        }


Text._unique_id = "Text-builtin"
