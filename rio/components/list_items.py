from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .component import Component
from .fundamental_component import FundamentalComponent

__all__ = [
    "CustomListItem",
    "HeadingListItem",
    "SimpleListItem",
]


class HeadingListItem(FundamentalComponent):
    """

    # HeadingListItem

    A list item with a header. Similar to `SimpleListItem` but without secondary text and additional components.
    on_press event is not supported.

    `Note:` check `rio.ListView` for more information on how to easily build this component.

    ## Attributes:
    `text:` The text to display.

    ## Example:
    A simple `HeadingListItem` with the text "Hello World!" will be shown:
    ```python
    rio.HeadingListItem("Hello World!")
    ```

    Lets assume you want to build a `ListView` with a list of products as Headers. You can easily
    build the list items with a for loop and add them to the `ListView`:

    ```python
    class ComponentClass(rio.Component):

        products: List[str] = ["Product 1", "Product 2", "Product 3"]

        def build(self)->rio.Component:
            list_items = []
            for product in self.products:
                list_items.append(rio.HeadingListItem(product))
            return rio.ListView(*list_items)
    ```
    """

    text: str


HeadingListItem._unique_id = "HeadingListItem-builtin"


class SimpleListItem(Component):
    """
    # SimpleListItem

    A simple list item with a header and optional secondary text. Additional components
    can be added to the left and right sides of the list item.

    `Note:` check `rio.ListView` for more information on how to easily build this component.
    Don't forget to add the `key` attribute to the `SimpleListItem` if you want to use it in
    a `ListView`. Therefor you can assure that the list item is properly rebuild.

    ## Attributes:
    `text:` The text to display.

    `secondary_text:` The secondary text to display.

    `left_child:` A component to display on the left side of the list item.

    `right_child:` A component to display on the right side of the list item.

    `on_press:` Triggered when the list item is pressed.

    ## Example:
    A simple `SimpleListItem` with the text "Click me!" will be shown:
    ```python
    rio.SimpleListItem("Click me!")
    ```

    Lets assume you want to build a `ListView` with a list of products. You can easily
    build the list items with a for loop and add them to the `ListView`. You can use
    `functools.partial` to pass the product to the `on_press` event handler:

    ```python
    import functools

    class ComponentClass(rio.Component):

        products: List[str] = ["Product 1", "Product 2", "Product 3"]

        def on_press_simple_list_item(self, product:str) -> None:
            print(f"Selected {product}")

        def build(self)->rio.Component:
            list_items = []
            for product in self.products:
                list_items.append(
                    rio.SimpleListItem(
                        text=product,
                        left_child=rio.Icon("castle"),
                        on_press=functools.partial(
                            self.on_press_simple_list_item,
                            product=product,
                        ),
                    )
                )
            return rio.ListView(*list_items)
    ```
    """

    text: str
    _: KW_ONLY
    secondary_text: str = ""
    left_child: rio.Component | None = None
    right_child: rio.Component | None = None
    on_press: rio.EventHandler[[]] = None

    def build(self) -> rio.Component:
        children = []

        # Left child
        if self.left_child is not None:
            children.append(self.left_child)

        # Main content (text)
        text_children = [
            rio.Text(
                self.text,
                align_x=0,
            )
        ]

        if self.secondary_text:
            text_children.append(
                rio.Text(
                    self.secondary_text,
                    multiline=True,
                    style="dim",
                    align_x=0,
                )
            )

        children.append(
            rio.Column(
                *text_children,
                spacing=0.5,
                width="grow",
                align_y=0.5,  # Prevent Undefined space
            )
        )

        # Right child
        if self.right_child is not None:
            children.append(self.right_child)

        # Combine everything
        return CustomListItem(
            content=rio.Row(
                *children,
                spacing=1,
                width="grow",
            ),
            on_press=self.on_press,
        )


class CustomListItem(FundamentalComponent):
    """
    # CustomListItem

    A list item with custom content.

    Most of the time the `SimpleListItem` will do the job. With `CustomListItems` you can
    build more complex list items. You can add any component to the list item. This can be e.g.
    a `Row`, `Column`, `Text`, `Icon`, `Image` or any other component.

    `Note:` check `rio.ListView` for more information on how to easily build this component.

    ## Attributes:
    `content:` The content to display.

    `on_press:` Triggered when the list item is pressed.

    ## Example:
    TODO: add example

    ```python

    ```
    """

    content: rio.Component
    _: KW_ONLY
    on_press: rio.EventHandler[[]] = None

    def _custom_serialize(self) -> JsonDoc:
        return {
            "pressable": self.on_press is not None,
        }

    async def _on_message(self, msg: Any) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg
        assert msg["type"] == "press", msg

        msg_type: str = msg["type"]
        assert isinstance(msg_type, str), msg_type

        if self.on_press is None:
            return

        # Trigger the press event
        await self.call_event_handler(self.on_press)

        # Refresh the session
        await self.session._refresh()


CustomListItem._unique_id = "CustomListItem-builtin"
