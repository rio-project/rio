from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "Dropdown",
    "DropdownChangeEvent",
]

T = TypeVar("T")


@dataclass
class DropdownChangeEvent(Generic[T]):
    value: T


class Dropdown(component_base.FundamentalComponent, Generic[T]):
    """
    A dropdown menu allowing the user to select one of several options.

    Dropdowns present the user with a list of options, allowing them to select
    exactly one. In their default state dropdowns are compact and display the
    currently selected option. When activated, a popup menu appears with a list
    of all available options.

    Attributes:
        options: A mapping from option names to values. The names are displayed
            in the dropdown menu, and the corresponding value is returned when
            the user selects the option. The values must be comparable.

        label: A short text to display next to the dropdown.

        selected_value: The value of the currently selected option.

        on_change: Triggered whenever the user selects an option.

        is_sensitive: Whether the dropdown should respond to user input.
    """

    options: Mapping[str, T]
    _: KW_ONLY
    label: str
    selected_value: T
    on_change: rio.EventHandler[DropdownChangeEvent[T]]
    is_sensitive: bool = True

    def __init__(
        self,
        options: Union[Mapping[str, T], Sequence[T]],
        *,
        label: str = "",
        selected_value: Optional[T] = None,
        on_change: rio.EventHandler[DropdownChangeEvent[T]] = None,
        is_sensitive: bool = True,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["natural", "grow"], float] = "natural",
        height: Union[Literal["natural", "grow"], float] = "natural",
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        if not options:
            raise ValueError("`Dropdown` must have at least one option.")

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

        if isinstance(options, Sequence):
            options = {str(value): value for value in options}

        self.options = options
        self.label = label
        self.on_change = on_change
        self.is_sensitive = is_sensitive

        # This is an unsafe assignment, because the value could be `None`. This
        # will be fixed in `on_create`, once the state bindings have been
        # initialized.
        self.selected_value = selected_value  # type: ignore

    @rio.event.on_create
    def _on_create(self) -> None:
        # Make sure a value is selected
        if self.selected_value is None:
            self.selected_value = next(iter(self.options.values()))

    def _fetch_selected_name(self) -> str:
        # The frontend works with names, not values. Get the corresponding
        # name.

        # Avoid hammering a potential state binding
        selected_value = self.selected_value

        # Fetch the name
        for name, value in self.options.items():
            if value == selected_value:
                return name
        else:
            # If nothing matches, just select the first option
            return next(iter(self.options.keys()))

    def _custom_serialize(self) -> JsonDoc:
        result: JsonDoc = {
            "optionNames": list(self.options.keys()),
            "selectedName": self._fetch_selected_name(),
        }

        return result

    async def _on_message(self, msg: Any) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg

        # The frontend works with names, not values. Get the corresponding
        # value.
        try:
            self.selected_value = self.options[msg["name"]]
        except KeyError:
            # Invalid names may be sent due to lag between the frontend and
            # backend. Ignore them.
            return

        # Trigger the event
        await self.call_event_handler(
            self.on_change, DropdownChangeEvent(self.selected_value)
        )

        # Refresh the session
        await self.session._refresh()


Dropdown._unique_id = "Dropdown-builtin"
