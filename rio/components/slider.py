from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from uniserde import JsonDoc

import rio

from .fundamental_component import FundamentalComponent

__all__ = [
    "Slider",
    "SliderChangeEvent",
]


@dataclass
class SliderChangeEvent:
    value: float


class Slider(FundamentalComponent):
    """
    # Slider
    A component for selecting a single value from a range.

    The `Slider` components allows the user to select a single real number value
    by dragging a handle along a line. The value can be any number within a
    range you can specify.

    ## Attributes:
    `minimum:` The minimum value the slider can be set to.

    `maximum:` The maximum value the slider can be set to.

    `value:` The current value of the slider.

    `is_sensitive:` Whether the slider should respond to user input.

    ## Example:
    A simple slider with a range from 0 to 100:
    ```python
    rio.Slider(
        minimum=0,
        maximum=100,
    )
    ```

    A simple slider with with a range from 0 to 100 and a step size of 1:
    ```python
    class Component(rio.Component):
        value:int = 0

        def build(self)->rio.Component:
            return rio.Slider(
                value=Component.value,
                minimum=0,
                maximum=100,
                step_size=1,
            )

    Or a slider with a range from 0 to 100 and a step size of 1, and a callback:
    ```python
    class Component(rio.Component):
        value:int = 0

        def on_change(self, event:rio.SliderChangeEvent):
            self.value = event.value

        def build(self)->rio.Component:
            return rio.Slider(
                value=self.value,
                minimum=0,
                maximum=100,
                step_size=1,
                on_change=self.on_change,
            )
    ```
    """

    minimum: float
    maximum: float
    value: float
    step_size: float
    is_sensitive: bool
    on_change: rio.EventHandler[SliderChangeEvent]

    def __init__(
        self,
        *,
        minimum: float = 0,
        maximum: float = 1,
        step_size: float = 0,
        value: float | None = None,
        is_sensitive: bool = True,
        on_change: rio.EventHandler[SliderChangeEvent] = None,
        key: str | None = None,
        margin: float | None = None,
        margin_x: float | None = None,
        margin_y: float | None = None,
        margin_left: float | None = None,
        margin_top: float | None = None,
        margin_right: float | None = None,
        margin_bottom: float | None = None,
        width: float | Literal["grow"] = 1.3,
        height: float | Literal["grow"] = 1.3,
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

        self.minimum = minimum
        self.maximum = maximum
        self.step_size = step_size
        self.value = value  # type: ignore  Possibly assigning None. Fixed in __post_init__ below
        self.is_sensitive = is_sensitive
        self.on_change = on_change

    def __post_init__(self) -> None:
        # Don't hammer potential state bindings
        minimum = self.minimum
        maximum = self.maximum
        step_size = self.step_size
        value = self.value

        initial_value = value

        if maximum <= minimum:
            raise ValueError(
                f"`maximum` must be greater than `minimum`. Got {maximum} <= {minimum}"
            )

        if step_size < 0:
            raise ValueError(
                f"`step_size` must be greater than or equal to 0. Got {step_size}"
            )

        if value is None:
            value = minimum + (maximum - minimum) / 2

        if step_size != 0:
            value = round(value / step_size) * step_size

        value = min(maximum, max(minimum, value))

        # Only assign the value if it has in fact changed, as this causes a
        # refresh. If the value is bound to the parent and the parent rebuilds
        # this creates an infinite loop.
        if value != initial_value:
            self.value = value

    # TODO: When `minimum` or `maximum` is changed, make sure the value is still within
    # the range

    def _validate_delta_state_from_frontend(self, delta_state: JsonDoc) -> None:
        if not set(delta_state) <= {"value"}:
            raise AssertionError(
                f"Frontend tried to change `{type(self).__name__}` state: {delta_state}"
            )

        if "value" in delta_state and not self.is_sensitive:
            raise AssertionError(
                f"Frontend tried to set `Slider.value` even though `is_sensitive` is `False`"
            )

    async def _call_event_handlers_for_delta_state(self, delta_state: JsonDoc) -> None:
        # Trigger on_change event
        try:
            new_value = delta_state["value"]
        except KeyError:
            pass
        else:
            assert isinstance(new_value, (int, float)), new_value
            await self.call_event_handler(
                self.on_change,
                SliderChangeEvent(new_value),
            )


Slider._unique_id = "Slider-builtin"
