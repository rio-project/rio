from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from . import component_base

__all__ = [
    "Slider",
]


class Slider(component_base.FundamentalComponent):
    """
    A component for selecting a single value from a range.

    The `Slider` components allows the user to select a single real number value
    by dragging a handle along a line. The value can be any number within a
    range you can specify.

    Attributes:
        min: The minimum value the slider can be set to.

        max: The maximum value the slider can be set to.

        value: The current value of the slider.

        is_sensitive: Whether the slider should respond to user input.
    """

    _: KW_ONLY
    min: float = 0
    max: float = 1
    value: float = 0.5
    is_sensitive: bool = True


Slider._unique_id = "Slider-builtin"
