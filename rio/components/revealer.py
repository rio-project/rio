from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import Literal, TypeVar

from uniserde import JsonDoc

import rio

from .fundamental_component import FundamentalComponent

__all__ = [
    "Revealer",
    "RevealerChangeEvent",
]

T = TypeVar("T")


@dataclass
class RevealerChangeEvent:
    is_open: bool


class Revealer(FundamentalComponent):
    """
    # Revealer

    A component that can be used to hide and reveal content.

    `Revealer` is a versatile component that can be used to hide and reveal
    content. It can be used to create collapsible sections, or to hide and
    reveal content based on user input.

    ## Attributes:
    `header:` The header of the `Revealer`. If `None`, the `Revealer` will be
            hidden by default.

    `content:` The content to display when the `Revealer` is open.

    `header_style:` The style of the header. Can be one of `"heading1"`,
            `"heading2"`, `"heading3"`, or `"text"`.

    `is_open:` Whether the `Revealer` is open or not.

    `on_change:` An event handler that is called when the `Revealer` is opened
            or closed. The event handler receives a `RevealerChangeEvent` as
            input.

    ## Example:
    A simple `Revealer` that displays a button when opened:
    ```python
    rio.Revealer(
        header="Click to reveal",
        content=rio.Button(
            content="Hello",
        ),
    )
    ```

    A `Revealer` that displays a `MultiLineTextInput` when opened and updates
    its text on change:
    ```python
    class Component(rio.Component):
        text: str = ""

        def build(self) -> rio.Component:
            return rio.Revealer(
                    header= "Click to Reveal",
                    content = rio.MultiLineTextInput(
                                label="Write your comments here",
                                text=Component.text,
                                ),
                    header_style = "heading2",
                    )
    ```

    A `Revealer` that displays a `MultiLineTextInput` when opened and updates
    its text on change:
    ```python

    class Component(rio.Component):
        text: str = ""

        def on_change_update_text(self, ev: rio.MultiLineTextInputChangeEvent):
            self.text = ev.text

        def build(self) -> rio.Component:
            return rio.Revealer(
                    header= "Click to Reveal",
                    content = rio.MultiLineTextInput(
                                label="Write your comments here",
                                text=self.text,
                                on_change=self.on_change_update_text,
                                ),
                    header_style = "heading2",
                    )
    ```
    """

    header: str | None
    content: rio.Component
    _: KW_ONLY
    header_style: (
        Literal["heading1", "heading2", "heading3", "text"] | rio.TextStyle
    ) = "text"
    is_open: bool = False
    on_change: rio.EventHandler[RevealerChangeEvent] = None

    def _validate_delta_state_from_frontend(self, delta_state: JsonDoc) -> None:
        if not set(delta_state) <= {"is_open"}:
            raise AssertionError(
                f"Frontend tried to change `{type(self).__name__}` state: {delta_state}"
            )

        if "is_open" in delta_state and self.header is None:
            raise AssertionError(
                f"Frontend tried to set `Revealer.is_open` even though it has no `header`"
            )

    async def _call_event_handlers_for_delta_state(self, delta_state: JsonDoc) -> None:
        # Trigger on_change event
        try:
            new_value = delta_state["is_open"]
        except KeyError:
            pass
        else:
            assert isinstance(new_value, bool), new_value
            await self.call_event_handler(
                self.on_change,
                RevealerChangeEvent(new_value),
            )

    def _custom_serialize(self) -> JsonDoc:
        # Serialization doesn't handle unions. Hence the custom serialization
        # here
        if isinstance(self.header_style, str):
            header_style = self.header_style
        else:
            header_style = self.header_style._serialize(self.session)

        return {
            "header_style": header_style,
        }


Revealer._unique_id = "Revealer-builtin"
