from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from . import component_base, progress_circle

__all__ = [
    "Button",
    "IconButton",
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
        child: The text or child component to display inside of the button.

        icon: The name of an icon to display on the button, in the form
            "set/name:variant". See the `Icon` component for details of how
            icons work in Rio.

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

    child: Union[rio.Component, str] = ""
    _: KW_ONLY
    icon: Optional[str] = None
    shape: Literal["pill", "rounded", "rectangle"] = "pill"
    style: Literal["major", "minor", "plain"] = "major"
    color: rio.ColorSet = "keep"
    is_sensitive: bool = True
    is_loading: bool = False
    initially_disabled_for: float = INITIALLY_DISABLED_FOR
    on_press: rio.EventHandler[[]] = None

    def build(self) -> rio.Component:
        # Prepare the child
        if self.is_loading:
            if self.color in ("keep", "secondary"):
                progress_color = "primary"
            else:
                progress_color = "secondary"

            child = progress_circle.ProgressCircle(
                size=1.5,
                align_x=0.5,
                margin=0.3,
                color=progress_color,
            )
        elif isinstance(self.child, component_base.Component):
            child = rio.Container(
                self.child,
                align_x=0.5,
            )
        elif self.icon is None:
            child = rio.Text(
                self.child.strip(),
                # Make sure there's no popping when switching between Text & ProgressCircle
                height=1.6,
                margin_x=0.7,
                margin_y=0.3,
            )
        else:
            child = rio.Row(
                rio.Icon(
                    self.icon,
                    height=1.4,
                    width=1.4,
                ),
                rio.Text(
                    self.child.strip(),
                    height=1.5,
                    width="grow",
                ),
                spacing=0.6,
                align_x=0.5,
                # Make sure there's no popping when switching between Text & ProgressCircle
                height=1.6,
                margin_x=0.7,
                margin_y=0.3,
            )

        # Delegate to a HTML Component
        return _ButtonInternal(
            on_press=self.on_press,
            child=child,
            shape=self.shape,
            style=self.style,
            color=self.color,
            is_sensitive=self.is_sensitive,
            is_loading=self.is_loading,
            width=8,
            initially_disabled_for=self.initially_disabled_for,
            square_aspect_ratio=False,
        )

    def __str__(self) -> str:
        if isinstance(self.child, str):
            text_or_child = f"text:{self.child!r}"
        else:
            text_or_child = f"child:{self.child._id}"

        return f"<Button id:{self._id} {text_or_child}>"


class IconButton(component_base.Component):
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
    style: Literal["major", "minor", "plain"]
    color: rio.ColorSet
    is_sensitive: bool
    on_press: rio.EventHandler[[]]
    initially_disabled_for: float = INITIALLY_DISABLED_FOR
    size: float

    def __init__(
        self,
        icon: str,
        *,
        style: Literal["major", "minor", "plain"] = "major",
        color: rio.ColorSet = "keep",
        is_sensitive: bool = True,
        on_press: rio.EventHandler[[]] = None,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        size: float = 3.7,
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        super().__init__(
            key=key,
            margin=margin,
            margin_x=margin_x,
            margin_y=margin_y,
            margin_left=margin_left,
            margin_top=margin_top,
            margin_right=margin_right,
            margin_bottom=margin_bottom,
            width="natural",
            height="natural",
            align_x=align_x,
            align_y=align_y,
        )

        self.icon = icon
        self.size = size
        self.style = style
        self.color = color
        self.is_sensitive = is_sensitive
        self.on_press = on_press
        self.initially_disabled_for = INITIALLY_DISABLED_FOR

    def build(self) -> rio.Component:
        return _ButtonInternal(
            on_press=self.on_press,
            child=rio.Icon(
                self.icon,
                height=self.size * 0.65,
                width=self.size * 0.65,
                align_x=0.5,
                align_y=0.5,
            ),
            shape="circle",
            style=self.style,
            color=self.color,
            is_sensitive=self.is_sensitive,
            is_loading=False,
            width=self.size,
            height=self.size,
            initially_disabled_for=self.initially_disabled_for,
            square_aspect_ratio=True,
        )


class _ButtonInternal(component_base.FundamentalComponent):
    _: KW_ONLY
    on_press: rio.EventHandler[[]]
    child: rio.Component
    shape: Literal["pill", "rounded", "rectangle", "circle"]
    style: Literal["major", "minor", "plain"]
    color: rio.ColorSet
    is_sensitive: bool
    is_loading: bool
    initially_disabled_for: float
    square_aspect_ratio: bool

    async def _on_message(self, msg: Any) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg
        assert msg["type"] == "press", msg

        msg_type: str = msg["type"]
        assert isinstance(msg_type, str), msg_type

        # Is the button sensitive?
        if not self.is_sensitive or self.is_loading:
            return

        # Trigger the press event
        await self.call_event_handler(self.on_press)

        # Refresh the session
        await self.session._refresh()


_ButtonInternal._unique_id = "Button-builtin"
