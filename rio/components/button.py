from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from . import component_base, progress_circle

__all__ = [
    "Button",
    "CircularButton",
]


INITIALLY_DISABLED_FOR = 0.25


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
    color: rio.ColorSet = "keep"
    is_sensitive: bool = True
    is_loading: bool = False
    initially_disabled_for: float = INITIALLY_DISABLED_FOR
    on_press: rio.EventHandler[[]] = None

    def build(self) -> rio.Component:
        # Prepare the child
        if self.is_loading:
            child = progress_circle.ProgressCircle(
                size=1.5,
                align_x=0.5,
                margin=0.3,
            )
        else:
            children: List[component_base.Component] = []

            if self.icon is not None:
                if self.shape == "circle":
                    icon_size = 2.2
                else:
                    icon_size = 1.2

                children.append(
                    rio.Icon(
                        self.icon,
                        height=icon_size,
                        width=icon_size,
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
                margin_x=0.7,
                margin_y=0.3,
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
            initially_disabled_for=self.initially_disabled_for,
        )

    def __str__(self) -> str:
        return f"<Button id:{self._id} text:{self.text!r}>"


class CircularButton(component_base.Component):
    """
    A round, clickable button with shadow.

    The `FloatingActionButton` component is similar to the `Button` component,
    but has a different visual style. It is round and has a shadow, making it
    appear to hover above the rest of the page. It is typically used to make the
    most important action on a page stand out. For example, an e-mail client
    might use a floating action button to compose a new e-mail. A note taking
    app might use it to create a new note.

    The `FloatingActionButton` itself doesn't perform any special layouting.
    Combine it with `rio.Stack` or `rio.Overlay` to make it float above other
    components.
    """

    icon: str
    _: KW_ONLY
    color: rio.ColorSet = "keep"
    is_sensitive: bool = True
    on_press: rio.EventHandler[[]] = None
    initially_disabled_for: float = INITIALLY_DISABLED_FOR

    def build(self) -> rio.Component:
        return _ButtonInternal(
            on_press=self.on_press,
            style="major",
            child=rio.Icon(
                self.icon,
                height=2.5,
                width=2.5,
                align_x=1,
                align_y=1,
            ),
            shape="circle",
            color=self.color,
            is_sensitive=self.is_sensitive,
            width=4,
            height=4,
            margin_right=3,
            margin_bottom=3,
            align_x=1,
            align_y=1,
            initially_disabled_for=self.initially_disabled_for,
        )


class _ButtonInternal(component_base.FundamentalComponent):
    _: KW_ONLY
    on_press: rio.EventHandler[[]]
    child: rio.Component
    shape: Literal["pill", "rounded", "rectangle", "circle"]
    style: Literal["major", "minor"]
    color: rio.ColorSet
    is_sensitive: bool
    initially_disabled_for: float

    async def _on_message(self, msg: Any) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg
        assert msg["type"] == "press", msg

        msg_type: str = msg["type"]
        assert isinstance(msg_type, str), msg_type

        # Is the button sensitive?
        if not self.is_sensitive:
            return

        # Trigger the press event
        await self.call_event_handler(self.on_press)

        # Refresh the session
        await self.session._refresh()


_ButtonInternal._unique_id = "Button-builtin"
