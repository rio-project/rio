from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

import babel.numbers

import rio

from . import component_base

__all__ = [
    "NumberInput",
    "NumberInputChangeEvent",
    "NumberInputConfirmEvent",
]


# These must be ints so that `integer * multiplier` returns an int and not a
# float
_multiplier_suffixes: Mapping[str, int] = {
    "k": 1_000,
    "m": 1_000_000,
}


@dataclass
class NumberInputChangeEvent:
    value: float


@dataclass
class NumberInputConfirmEvent:
    value: float


class NumberInput(component_base.Component):
    """
    Like `TextInput`, but specifically for inputting numbers.

    `NumberInput` allows the user to enter a number. This is similar to the
    `TextInput` component, but with some goodies for handling numbers. The value
    is automatically parsed and formatted according to the user's locale, and
    you can specify minimum and maximum values to limit the user's input.

    Number inputs go way beyond just parsing the input using `int` or `float`.
    They try their best to understand what the user is trying to enter, and also
    support suffixes such as "k" and "m" to represent thousands and millions
    respectively.

    Attributes:
        value: The number currently entered by the user.

        label: A short text to display next to the text input.

        prefix_text: A short text to display before the text input. Useful for
            displaying currency symbols or other prefixed units.

        suffix_text: A short text to display after the text input. Useful for
            displaying currency names or units.

        minimum: The minimum value the number can be set to.

        maximum: The maximum value the number can be set to.

        decimals: The number of decimals to accept. If the user enters more
            decimals, they will be rounded off. If this value is equal to `0`,
            the input's `value` is guaranteed to be an integer, rather than
            float.

        on_change: Triggered when the user changes the number.

        on_confirm: Triggered when the user explicitly confirms their input,
    """

    value: float = 0
    _: KW_ONLY
    label: str = ""
    prefix_text: str = ""
    suffix_text: str = ""
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    decimals: int = 2
    on_change: rio.EventHandler[NumberInputChangeEvent] = None
    on_confirm: rio.EventHandler[NumberInputConfirmEvent] = None

    def __post_init__(self):
        self._text_input = None

    def _try_set_value(self, raw_value: str) -> bool:
        """
        Parse the given string and update the component's value accordingly.
        Returns `True` if the value was successfully updated, `False` otherwise.
        """

        # Strip the number down as much as possible
        locale = self.session.preferred_locales[0]
        raw_value = raw_value.strip()

        # Try to parse the value
        if not raw_value:
            return False

        decimals = self.decimals

        # Check for a multiplier suffix
        suffix = raw_value[-1].lower()
        multiplier = 1

        if suffix.isalpha():
            try:
                multiplier = _multiplier_suffixes[suffix]
            except KeyError:
                pass
            else:
                raw_value = raw_value[:-1].rstrip()

        # Try to parse the number
        try:
            if self.decimals == 0:
                value = babel.numbers.parse_number(raw_value, locale)
            else:
                value = float(
                    babel.numbers.parse_decimal(raw_value, locale, strict=True)
                )
        except babel.numbers.NumberFormatError:
            return False

        # Apply the multiplier
        value *= multiplier

        # Limit the number of decimals
        #
        # Ensure the value is an integer, if the number of decimals is 0
        value = round(value, None if decimals == 0 else decimals)

        # Clamp the value
        minimum = self.minimum
        if minimum is not None:
            value = max(value, minimum)

        maximum = self.maximum
        if maximum is not None:
            value = min(value, maximum)

        # Update the value
        self.value = value
        return True

    async def _on_change(self, ev: rio.TextInputChangeEvent) -> None:
        was_updated = self._try_set_value(ev.text)

        if was_updated:
            await self.call_event_handler(
                self.on_change,
                NumberInputChangeEvent(self.value),
            )

    async def _on_confirm(self, ev: rio.TextInputConfirmEvent) -> None:
        was_updated = self._try_set_value(ev.text)

        if was_updated:
            await self.call_event_handler(
                self.on_confirm,
                NumberInputConfirmEvent(self.value),
            )

    def build(self) -> rio.Component:
        # Format the number
        locale = self.session.preferred_locales[0]

        decimals = self.decimals
        if decimals == 0:
            value_str = babel.numbers.format_number(self.value, locale)
        else:
            value_str = babel.numbers.format_decimal(
                self.value,
                "#,##0." + "#" * decimals,
                locale,
            )

        # Build the component
        self._text_input = rio.TextInput(
            text=value_str,
            label=self.label,
            prefix_text=self.prefix_text,
            suffix_text=self.suffix_text,
            on_change=self._on_change,
            on_confirm=self._on_confirm,
        )
        return self._text_input

    async def grab_keyboard_focus(self) -> None:
        if self._text_input is not None:
            await self._text_input.grab_keyboard_focus()
