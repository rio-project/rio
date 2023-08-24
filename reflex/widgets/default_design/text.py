from typing import *  # type: ignore

from uniserde import JsonDoc

import reflex as rx

from . import theme

__all__ = [
    "Text",
]


from dataclasses import KW_ONLY
from typing import *  # type: ignore

import reflex as rx

from .. import fundamental
from . import theme

__all__ = [
    "Text",
]


class Text(fundamental.widget_base.HtmlWidget):
    text: str
    _: KW_ONLY
    multiline: bool = False
    style: Optional[rx.TextStyle] = None

    def _custom_serialize(self) -> JsonDoc:
        # If a custom style is set, there is nothing to do
        if self.style is not None:
            return {}

        # Otherwise fetch and serialize the style from the theme
        thm = self.session.attachments[theme.Theme]
        return {
            "style": thm.text_style._serialize(),
        }


Text._unique_id = "Text-builtin"
