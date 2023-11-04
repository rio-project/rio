from __future__ import annotations

from dataclasses import dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "Slider",
    "SliderChangeEvent",
]


T = TypeVar("T", bound=float)


@dataclass
class SliderChangeEvent(Generic[T]):
    value: T


class Slider(component_base.FundamentalComponent, Generic[T]):
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

    min: T
    max: T
    value: T
    discrete: bool
    is_sensitive: bool
    on_change: rio.EventHandler[SliderChangeEvent[T]]

    @overload
    def __new__(
        cls,
        *,
        min: int = 0,
        max: int = 100,
        value: Optional[int] = None,
        discrete: Literal[True] = True,
        is_sensitive: bool = True,
        on_change: rio.EventHandler[SliderChangeEvent[int]] = None,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["grow"], float] = 1.3,
        height: Union[Literal["grow"], float] = 1.3,
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ) -> Slider[int]:
        ...

    @overload
    def __new__(
        cls,
        *,
        min: float = 0,
        max: float = 1,
        value: Optional[float] = None,
        discrete: bool = False,
        is_sensitive: bool = True,
        on_change: rio.EventHandler[SliderChangeEvent[float]] = None,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["grow"], float] = 1.3,
        height: Union[Literal["grow"], float] = 1.3,
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ) -> Slider[float]:
        ...

    def __new__(cls, *args, **kwargs):  # type: ignore
        return super().__new__(cls)

    def __init__(
        self,
        *,
        min: Optional[float] = None,
        max: Optional[float] = None,
        value: Optional[float] = None,
        discrete: bool = False,
        is_sensitive: bool = True,
        on_change: rio.EventHandler[SliderChangeEvent[T]] = None,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["grow"], float] = 1.3,
        height: Union[Literal["grow"], float] = 1.3,
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
            width=width,
            height=height,
            align_x=align_x,
            align_y=align_y,
        )

        if min is None:
            min = 0

        if max is None:
            max = 100 if discrete else 1

        if value is None:
            value = min + (max - min) / 2

            if discrete:
                value = round(value)

        self.min = min  # type: ignore
        self.max = max  # type: ignore
        self.value = value  # type: ignore
        self.discrete = discrete
        self.is_sensitive = is_sensitive
        self.on_change = on_change

    # TODO: When `min` or `max` is changed, make sure the value is still within
    # the range

    def _custom_serialize(self) -> JsonDoc:
        return {
            "min": self.min,
            "max": self.max,
            "value": self.value,
        }

    async def _on_state_update(self, delta_state: JsonDoc) -> None:
        # Trigger on_change event
        try:
            new_value = delta_state["value"]
        except KeyError:
            pass
        else:
            assert isinstance(new_value, (int, float)), new_value
            await self.call_event_handler(
                self.on_change,  # type: ignore
                SliderChangeEvent(new_value),
            )

        # Chain up
        await super()._on_state_update(delta_state)


Slider._unique_id = "Slider-builtin"
