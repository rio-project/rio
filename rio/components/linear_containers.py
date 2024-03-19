from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from uniserde import JsonDoc

import rio

from .fundamental_component import FundamentalComponent

__all__ = [
    "Row",
    "Column",
]


class _LinearContainer(FundamentalComponent):
    children: list[rio.Component]
    spacing: float = 0.0
    proportions: Literal["homogeneous"] | Sequence[float] | None = None

    # Don't let @dataclass generate a constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _custom_serialize(self) -> JsonDoc:
        return {"proportions": self.proportions}  # type: ignore[variance]


class Row(_LinearContainer):
    """
    # Row
    A container that lays out its children horizontally.

    `Row`s are one of the most common components in Rio. They take any number of
    children and lay them out horizontally, with the first one on the left, the
    second one to its right, and so on. All components in `Row`s occupy the full
    height of their parent.

    The `Row`'s horizontal counterpart is the `Column`. A similar component, but
    stacking its children in the Z direction, is the `Stack`.

    ### Undefined Space

    Like most containers in `rio`, `Row`s always attempt to allocate all
    available space to their children. In the context of a `Row` though, this
    could easily lead to unexpected results. If more space is available than
    needed, should all children grow? Only the first? Should they grow by equal
    amounts, or proportionally?

    To avoid this ambiguity, `Row`s have a concept of *undefined space*. Simply
    put, **not using all available space is considered an error and should be
    avoided.** `Row`s indicate this by highlighting the extra space with
    unmistakable animated sprites.

    Getting rid of undefined space is easy: Depending on what look you're going
    for, either add a `Spacer` somewhere into your `Row`, assign one of the
    components a `"grow"` value as its height, or set the `Row`'s vertical
    alignment.

    ## Attributes:
    `children:` The components to place in this `Row`.

    `spacing:` How much empty space to leave between two adjacent children. No
            spacing is added before the first child or after the last child.

    ## Example:

    A `Row` with two `Text` components and spacing between them:
    ```python
    rio.Row(
        rio.Text("Hello"),
        rio.Text("World!"),
        spacing=1,
    )
    ```

    A `Row` is used to place an `Icon` and two `Text` components in a Row. A `Card` with text
    and an icon in it, which is elevated when the mouse hovers over it and prints a message
    when clicked:
    ```python
    class Component(rio.Component):
        def on_press_card(self) -> None:
            print("Card was pressed!")

        def build(self)->rio.Component:
            card_content = rio.Row(
                rio.Icon(icon="castle"),
                rio.Text("Hello"),
                rio.Text("World!"),
                spacing=1,
                align_x=0.5,  # align card content in the center
            )
            return rio.Card(
                content=card_content,
                on_press=self.on_press_card,
                elevate_on_hover=True,
                color="primary",
            )
    ```
    """

    def __init__(
        self,
        *children: rio.Component,
        spacing: float = 0.0,
        proportions: Literal["homogeneous"] | Sequence[float] | None = None,
        key: str | None = None,
        margin: float | None = None,
        margin_x: float | None = None,
        margin_y: float | None = None,
        margin_left: float | None = None,
        margin_top: float | None = None,
        margin_right: float | None = None,
        margin_bottom: float | None = None,
        width: float | Literal["natural", "grow"] = "natural",
        height: float | Literal["natural", "grow"] = "natural",
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
            width=width,
            height=height,
            align_x=align_x,
            align_y=align_y,
        )

        self.children = list(children)
        self.spacing = spacing
        self.proportions = proportions


Row._unique_id = "Row-builtin"


class Column(_LinearContainer):
    """
    # Column
    A container that lays out its children vertically.

    `Column`s are one of the most common components in Rio. They take any number
    of children and lay them out vertically, with the first one at the top, the
    second one below that, and so on. All components in `Column`s occupy the
    full width of their parent.

    The `Column`'s horizontal counterpart is the `Row`. A similar component, but
    stacking its children in the Z direction, is the `Stack`.

    ### Undefined Space

    Like most containers in `rio`, `Column`s always attempt to allocate all
    available space to their children. In the context of a `Column` though, this
    could easily lead to unexpected results. If more space is available than
    needed, should all children grow? Only the first? Should they grow by equal
    amounts, or proportionally?

    To avoid this ambiguity, `Column`s have a concept of *undefined space*.
    Simply put, **not using all available space is considered an error and
    should be avoided.** `Column`s indicate this by highlighting the extra space
    with unmistakable animated sprites.

    Getting rid of undefined space is easy: Depending on what look you're going
    for, either add a `Spacer` somewhere into your `Column`, assign one of the
    components a `"grow"` value as its height, or set the `Column`'s vertical
    alignment.

    ## Attributes:
    `children:` The components to place in this `Column`.

    `spacing:` How much empty space to leave between two adjacent children. No
            spacing is added before the first child or after the last child.

    ## Example:
    A `Column` with two `Text` components and spacing between them:
    ```python
    rio.Column(
        rio.Text("Hello"),
        rio.Text("World!"),
        spacing=1,
    )
    ```

    A `Column` is used to place an `Icon` and two `Text` components in a Column. A `Card` with text
    and an icon in it, which is elevated when the mouse hovers over it and prints a message
    when clicked:
    ```python
    class ComponentClass(rio.Component):
        def on_press_card(self) -> None:
            print("Card was pressed!")

        def build(self) -> rio.Component:
            card_content = rio.Column(
                rio.Icon(icon="castle"),
                rio.Text("Hello"),
                rio.Text("World!"),
                spacing=1,
                align_x=0.5,  # align card content in the center
            )
            return rio.Card(
                content=card_content,
                on_press=self.on_press_card,
                elevate_on_hover=True,
                color="primary",
            )
    ```
    """

    def __init__(
        self,
        *children: rio.Component,
        spacing: float = 0.0,
        proportions: Literal["homogeneous"] | Sequence[float] | None = None,
        key: str | None = None,
        margin: float | None = None,
        margin_x: float | None = None,
        margin_y: float | None = None,
        margin_left: float | None = None,
        margin_top: float | None = None,
        margin_right: float | None = None,
        margin_bottom: float | None = None,
        width: float | Literal["natural", "grow"] = "natural",
        height: float | Literal["natural", "grow"] = "natural",
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
            width=width,
            height=height,
            align_x=align_x,
            align_y=align_y,
        )

        self.children = list(children)
        self.spacing = spacing
        self.proportions = proportions


Column._unique_id = "Column-builtin"
