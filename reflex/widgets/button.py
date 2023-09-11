from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore
from typing import Optional

import reflex as rx

from . import progress_circle, widget_base

__all__ = [
    "Button",
    "ButtonPressEvent",
]


@dataclass
class ButtonPressEvent:
    pass


class Button(widget_base.Widget):
    text: str = ""
    _: KW_ONLY
    on_press: rx.EventHandler[ButtonPressEvent] = None
    icon: Optional[str] = None
    child: Optional[rx.Widget] = None
    shape: Literal["pill", "rounded", "rectangle", "circle"] = "pill"
    style: Literal["major", "minor"] = "major"
    color: rx.ColorSet = "primary"
    is_sensitive: bool = True
    is_loading: bool = False

    def build(self) -> rx.Widget:
        # Prepare the child
        if self.is_loading:
            child = progress_circle.ProgressCircle(
                size=1.5,
                align_x=0.5,
                margin=0.3,
                color="accent",
            )
        else:
            children = []

            if self.icon is not None:
                children.append(
                    rx.Icon(
                        self.icon,
                        height=1.2,
                        width=1.2,
                    )
                )

            stripped_text = self.text.strip()
            if stripped_text:
                children.append(
                    rx.Text(
                        stripped_text,
                        height=1.5,
                        width="grow",
                    )
                )

            if self.child is not None:
                children.append(self.child)

            child = rx.Row(
                *children,
                spacing=0.6,
                margin=0.2,
                align_x=0.5,
            )

        # Delegate to a HTML Widget
        return _ButtonInternal(
            on_press=self.on_press,
            child=child,
            shape=self.shape,
            style=self.style,
            color=self.color,
            is_sensitive=self.is_sensitive and not self.is_loading,
        )

    def __str__(self) -> str:
        return f"<Button id:{self._id} text:{self.text!r}>"


class _ButtonInternal(widget_base.HtmlWidget):
    _: KW_ONLY
    on_press: rx.EventHandler[ButtonPressEvent]
    child: rx.Widget
    shape: Literal["pill", "rounded", "rectangle", "circle"]
    style: Literal["major", "minor"]
    color: rx.ColorSet
    is_sensitive: bool

    async def _on_message(self, msg: Any) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg
        assert msg["type"] == "press", msg

        msg_type = msg["type"]
        assert isinstance(msg_type, str), msg_type

        # Is the button sensitive?
        if not self.is_sensitive:
            return

        # Trigger the press event
        await self._call_event_handler(
            self.on_press,
            ButtonPressEvent(),
        )

        # Refresh the session
        await self.session._refresh()


_ButtonInternal._unique_id = "Button-builtin"
