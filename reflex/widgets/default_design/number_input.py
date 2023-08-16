from __future__ import annotations

from dataclasses import dataclass, KW_ONLY
from typing import *  # type: ignore
from typing import Optional
from .. import fundamental

import reflex as rx

__all__ = [
    "NumberInput",
    "NumberInputChangeEvent",
    "NumberInputConfirmEvent",
]


_multiplier_suffixes = {
    "k": 1e3,
    "m": 1e6,
}


@dataclass
class NumberInputChangeEvent:
    value: float


@dataclass
class NumberInputConfirmEvent:
    value: float


class NumberInput(rx.Widget):
    value: float = 0
    placeholder: str = ""
    _: KW_ONLY
    round_to_integer: bool = False
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    thousands_separator: str = ","
    decimal_separator: str = "."
    decimals: int = 2
    on_change: fundamental.EventHandler[NumberInputChangeEvent] = None
    on_confirm: fundamental.EventHandler[NumberInputConfirmEvent] = None

    def _try_set_value(self, raw_value: str) -> bool:
        """
        Parse the given string and update the widget's value accordingly.
        Returns `True` if the value was successfully updated, `False` otherwise.
        """

        # Strip the number down as much as possible
        raw_value = raw_value.strip()
        raw_value = raw_value.replace(self.thousands_separator, "")

        # Allow followup code to assume there is a value
        if not raw_value:
            self.value = self.value  # Force the old value to stay
            return False

        # Check for a multiplier suffix
        suffix = raw_value[-1].lower()
        multiplier = 1

        if suffix.isalpha():
            try:
                multiplier = _multiplier_suffixes[suffix]
            except KeyError:
                pass
            else:
                raw_value = raw_value[:-1]

        # Try to parse the number
        try:
            value = float(raw_value.replace(self.decimal_separator, "."))
        except ValueError:
            self.value = self.value  # Force the old value to stay
            return False

        # Apply the multiplier
        value *= multiplier

        # Integer?
        if self.round_to_integer:
            value = round(value)

        # Clamp the value
        if self.minimum is not None:
            value = max(value, self.minimum)

        if self.maximum is not None:
            value = min(value, self.maximum)

        # Update the value
        self.value = value
        return True

    async def _on_change(self, ev: fundamental.TextInputChangeEvent) -> None:
        was_updated = self._try_set_value(ev.text)

        if was_updated:
            await self._call_event_handler(
                self.on_change,
                NumberInputChangeEvent(self.value),
            )

    async def _on_confirm(self, ev: fundamental.TextInputConfirmEvent) -> None:
        was_updated = self._try_set_value(ev.text)

        if was_updated:
            await self._call_event_handler(
                self.on_confirm,
                NumberInputConfirmEvent(self.value),
            )

    def build(self) -> rx.Widget:
        # Format the number
        value_str = f"{self.value:.{self.decimals}f}"
        value_str = value_str.replace(".", self.decimal_separator)
        int_str, frac_str = value_str.split(self.decimal_separator)

        # Add thousands separators
        groups = []
        while len(int_str) > 3:
            groups.append(int_str[-3:])
            int_str = int_str[:-3]

        groups.append(int_str)
        int_str = self.thousands_separator.join(reversed(groups))

        # Join the strings
        if self.round_to_integer:
            value_str = int_str
        else:
            value_str = int_str + self.decimal_separator + frac_str

        # Build the widget
        return fundamental.TextInput(
            text=value_str,
            placeholder=self.placeholder,
            on_change=self._on_change,
            on_confirm=self._on_confirm,
        )
