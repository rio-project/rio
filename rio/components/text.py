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
    text: str
    _: KW_ONLY
    multiline: bool = False
    style: Union[
        Literal["heading1", "heading2", "heading3", "text"],
        text_style.TextStyle,
    ] = "text"

    def _custom_serialize(self) -> JsonDoc:
        # Serialization doesn't handle unions. Hence the custom serialization
        # here
        if isinstance(self.style, str):
            style = self.style
        else:
            style = self.session._serialize_and_host_value(
                self.style,
                text_style.TextStyle,
            )

        return {
            "style": style,
        }


Text._unique_id = "Text-builtin"
