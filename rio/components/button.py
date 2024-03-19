from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from .component import Component
from .fundamental_component import FundamentalComponent
from .progress_circle import ProgressCircle

__all__ = [
    "Button",
    "IconButton",
]


CHILD_MARGIN_X = 1.0
CHILD_MARGIN_Y = 0.3
INITIALLY_DISABLED_FOR = 0.25


class Button(Component):
    """
    # Button
    A clickable button.

    The `Button` component allows the user to trigger an action by clicking on
    it. You can use it to trigger a function call, navigate to a different page,
    or perform other actions.

    A similar, but more customizable component is `CustomButton`. Use that if
    you need more control over the button's visuals, e.g. for creating a
    navigation button.

    ## Attributes:
    `content`: The text or child component to display inside of the button.

    `icon:` The name of an icon to display on the button, in the form
            "set/name:variant". See the `Icon` component for details of how
            icons work in Rio.

    `shape:` The shape of the button. This can be one of:
    - `pill`: A rectangle where the left and right sides are completely round.
    - `rounded`: A rectangle with rounded corners.
    - `rectangle`: A rectangle with sharp corners.

    `style:` Controls the button's appearance. This can be one of:
    - `major`: A highly visible button with bold visuals.
    - `minor`: A less visible button that blends into the background.
    - `plain`: A button with no background or border. Use this to make
                       the button look like a link.

    `color:` The color scheme to use for the button.

    `is_sensitive:` Whether the button should respond to user input.

    `is_loading:` Whether the button should display a loading indicator. Use
            this to indicate to the user that an action is currently running.

    `initially_disabled_for:` The number of seconds the button should be
            disabled for after it is first rendered. This is useful to prevent
            the user from accidentally triggering an action when the page is
            first loaded.

    `on_press:` Triggered when the user clicks on the button.

    ## Example:
    A simple button with a castle icon:
    ```python
    rio.Button(
        content="Click me!",
        icon="castle",
    )
    ```

    The same button, but with a callback which prints "Button pressed!" to the console:
    ```python
    class ComponentClass(rio.Component):
            def on_press_button(self) -> None:
                print("Button pressed!")

            def build(self)->rio.Component:
                return rio.Button(
                        content="Click me!",
                        on_press=self.on_press_button,
                    )
    ```

    A button combined with a banner, which displays a message when the button is pressed:
    `Note:` If the banner_text is an empty string, the banner will disappear entirely.

    ```python
    class ComponentClass(rio.Component):
        banner_text: str = ""

        def on_press_button(self) -> None:
            self.banner_text = "Button pressed!"

        def build(self)->rio.Component:
            return rio.Column(
                rio.Banner(
                    text=self.banner_text,
                    style="info",
                ),
                rio.Button(
                    content="Click me!",
                    on_press=self.on_press_button,
                ),
                spacing=1,
            )
    ```
    """

    content: rio.Component | str = ""
    _: KW_ONLY
    icon: str | None = None
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

            child = ProgressCircle(
                size=1.5,
                align_x=0.5,
                margin_x=CHILD_MARGIN_Y,
                margin_y=CHILD_MARGIN_Y,
                color=progress_color,
            )
        elif isinstance(self.content, Component):
            child = rio.Container(
                self.content,
                margin_x=CHILD_MARGIN_Y,
                margin_y=CHILD_MARGIN_Y,
                align_x=0.5,
            )
        else:
            children = []
            text = self.content.strip()
            n_children = (self.icon is not None) + bool(text)

            if self.icon is not None:
                children.append(
                    rio.Icon(
                        self.icon,
                        width=1.4,
                        height=1.4,
                        margin_x=CHILD_MARGIN_X if n_children == 1 else None,
                        margin_y=CHILD_MARGIN_Y if n_children == 1 else None,
                    )
                )

            if text:
                children.append(
                    rio.Text(
                        text,
                        margin_x=CHILD_MARGIN_X if n_children == 1 else None,
                        margin_y=CHILD_MARGIN_Y if n_children == 1 else None,
                    )
                )

            if len(children) == 1:
                child = children[0]
            else:
                child = rio.Row(
                    *children,
                    spacing=0.6,
                    margin_x=CHILD_MARGIN_X,
                    margin_y=CHILD_MARGIN_Y,
                    align_x=0.5,
                )

        # Delegate to a HTML Component
        has_content = not isinstance(self.content, str) or self.content

        return _ButtonInternal(
            on_press=self.on_press,
            content=child,
            shape=self.shape,
            style=self.style,
            color=self.color,
            is_sensitive=self.is_sensitive,
            is_loading=self.is_loading,
            initially_disabled_for=self.initially_disabled_for,
            width=8 if has_content else 4,
            height=2.2,
        )

    def __str__(self) -> str:
        if isinstance(self.content, str):
            content = f"text:{self.content!r}"
        else:
            content = f"content:{self.content._id}"

        return f"<Button id:{self._id} {content}>"


class IconButton(Component):
    """
    # IconButton

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

    ## Attributes:
    `icon:` The name of an icon to display on the button, in the form
            "set/name:variant". See the `Icon` component for details of how
            icons work in Rio.

    `style:` Controls the button's appearance. This can be one of:
    - `major`: A highly visible button with bold visuals.
    - `minor`: A less visible button that blends into the background.
    - `plain`: A button with no background or border. Use this to make
                       the button look like a link.

    `color:` The color scheme to use for the button.

    `is_sensitive:` Whether the button should respond to user input.

    `initially_disabled_for:` The number of seconds the button should be
            disabled for after it is first rendered. This is useful to prevent
            the user from accidentally triggering an action when the page is
            first loaded.

    `size:` The size of the button. This is the diameter of the button in
            font-size units.

    `on_press:` Triggered when the user clicks on the button.

    ## Example:
    A simple `IconButton` with a castle icon:

    ```python
    rio.IconButton(
        icon="castle",
        style="major",
    )
    ```

    The same button, but with a callback which prints "Icon button pressed!" to the console:
    ```python
    class ComponentClass(rio.Component):
            def on_press_button(self) -> None:
                print("Icon button pressed!")

            def build(self)->rio.Component:
                return rio.IconButton(
                        icon="castle",
                        on_press=self.on_press_button,
                    )
    ```

    A button combined with a banner, which displays a message when the button is pressed:
    `Note:` If the banner_text is an empty string, the banner will disappear entirely.

    ```python
    class ComponentClass(rio.Component):
        banner_text: str = ""

        def on_press_button(self) -> None:
            self.banner_text = "Icon button pressed!"

        def build(self)->rio.Component:
            return rio.Column(
                rio.Banner(
                    text=self.banner_text,
                    style="info",
                ),
                rio.IconButton(
                    icon="castle",
                    on_press=self.on_press_button,
                ),
                spacing=1,
            )
    ```

    """

    icon: str
    _: KW_ONLY
    style: Literal["major", "minor", "plain"]
    color: rio.ColorSet
    is_sensitive: bool
    initially_disabled_for: float = INITIALLY_DISABLED_FOR
    size: float
    on_press: rio.EventHandler[[]]

    def __init__(
        self,
        icon: str,
        *,
        style: Literal["major", "minor", "plain"] = "major",
        color: rio.ColorSet = "keep",
        is_sensitive: bool = True,
        on_press: rio.EventHandler[[]] = None,
        key: str | None = None,
        margin: float | None = None,
        margin_x: float | None = None,
        margin_y: float | None = None,
        margin_left: float | None = None,
        margin_top: float | None = None,
        margin_right: float | None = None,
        margin_bottom: float | None = None,
        size: float = 3.7,
        align_x: float | None = None,
        align_y: float | None = None,
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
            content=rio.Icon(
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
            # Make sure the button has a square aspect ratio
            align_x=0.5,
            align_y=0.5,
        )

    def get_debug_details(self) -> dict[str, Any]:
        result = super().get_debug_details()

        # `width` & `height` are replaced with `size`
        del result["width"]
        del result["height"]

        return result


class _ButtonInternal(FundamentalComponent):
    _: KW_ONLY
    on_press: rio.EventHandler[[]]
    content: rio.Component
    shape: Literal["pill", "rounded", "rectangle", "circle"]
    style: Literal["major", "minor", "plain"]
    color: rio.ColorSet
    is_sensitive: bool
    is_loading: bool
    initially_disabled_for: float

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
