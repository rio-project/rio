from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

import rio

from . import component_base, progress_circle

__all__ = [
    "Button",
    "ButtonPressEvent",
]


@dataclass
class ButtonPressEvent:
    pass


class Button(component_base.Component):
    """
    A clickable button.

    The `Button` component allows the user to trigger an action by clicking on
    it. You can use it to trigger a function call, navigate to a different page,
    or perform other actions.

    A similar, but more customizable component is `CustomButton`. Use that if
    you need more control over the button's visuals, e.g. for creating a
    navigation button.

    Attributes:
        text: The text to display on the button.

        icon: The name of an icon to display on the button, in the form
            "set/name:variant". See the `Icon` component for details of how
            icons work in Rio.

        child: A component to display inside the button. This can be used to
            create more complex buttons than just icons and text.

        shape: The shape of the button. This can be one of:
            - `pill`: A rectangle where the left and right sides are completely
              round.
            - `rounded`: A rectangle with rounded corners.
            - `rectangle`: A rectangle with sharp corners.
            - `circle`: An ellipse. Make sure to control the button's width and
              height to make it a perfect circle.

        style: Controls the button's appearance. This can be one of:
            - `major`: A highly visible button with bold visuals.
            - `minor`: A less visible button that blends into the background.

        color: The color scheme to use for the button.

        is_sensitive: Whether the button should respond to user input.

        is_loading: Whether the button should display a loading indicator. Use
            this to indicate to the user that an action is currently running.

        on_press: Triggered when the user clicks on the button.
    """

    text: str = ""
    _: KW_ONLY
    icon: Optional[str] = None
    child: Optional[rio.Component] = None
    shape: Literal["pill", "rounded", "rectangle", "circle"] = "pill"
    style: Literal["major", "minor"] = "major"
    color: rio.ColorSet = "primary"
    is_sensitive: bool = True
    is_loading: bool = False
    on_press: rio.EventHandler[ButtonPressEvent] = None

    def build(self) -> rio.Component:
        # Prepare the child
        if self.is_loading:
            child = progress_circle.ProgressCircle(
                size=1.5,
                align_x=0.5,
                margin=0.3,
                color="secondary",
            )
        else:
            children: List[component_base.Component] = []

            if self.icon is not None:
                children.append(
                    rio.Icon(
                        self.icon,
                        height=1.2,
                        width=1.2,
                    )
                )

            stripped_text = self.text.strip()
            if stripped_text:
                children.append(
                    rio.Text(
                        stripped_text,
                        height=1.5,
                        width="grow",
                    )
                )

            if self.child is not None:
                children.append(self.child)

            child = rio.Row(
                *children,
                spacing=0.6,
                margin=0.3,
                align_x=0.5,
                # Make sure there's no popping when switching between Text & ProgressCircle
                height=1.6,
            )

        # Delegate to a HTML Component
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


class _ButtonInternal(component_base.FundamentalComponent):
    _: KW_ONLY
    on_press: rio.EventHandler[ButtonPressEvent]
    child: rio.Component
    shape: Literal["pill", "rounded", "rectangle", "circle"]
    style: Literal["major", "minor"]
    color: rio.ColorSet
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
        await self.call_event_handler(
            self.on_press,
            ButtonPressEvent(),
        )

        # Refresh the session
        await self.session._refresh()


_ButtonInternal._unique_id = "Button-builtin"
