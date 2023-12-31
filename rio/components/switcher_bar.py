from __future__ import annotations

from collections.abc import Mapping
from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .. import icon_registry
from . import component_base

__all__ = [
    "SwitcherBarChangeEvent",
    "SwitcherBar",
]

T = TypeVar("T")


@dataclass
class SwitcherBarChangeEvent(Generic[T]):
    value: Optional[T]


class SwitcherBar(component_base.FundamentalComponent, Generic[T]):
    names: List[str]
    values: List[T]
    icon_svg_sources: List[Optional[str]]
    color: rio.ColorSet
    orientation: Literal["horizontal", "vertical"]
    spacing: float
    selected_value: Optional[T]
    allow_none: bool
    on_change: rio.EventHandler[SwitcherBarChangeEvent[T]]

    def __init__(
        self,
        values: List[T],
        *,
        names: Optional[List[str]] = None,
        icons: Optional[Sequence[Optional[str]]] = None,
        color: rio.ColorSet = "keep",
        orientation: Literal["horizontal", "vertical"] = "horizontal",
        spacing: float = 1.0,
        allow_none: bool = False,
        selected_value: Optional[T] = None,
        on_change: rio.EventHandler[SwitcherBarChangeEvent[T]] = None,
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
        if not values:
            raise ValueError("`SwitcherBar` must have at least one option.")

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

        self.values = values
        self.color = color
        self.orientation = orientation
        self.spacing = spacing
        self.allow_none = allow_none
        self.on_change = on_change

        # Names default to the string representation of the values
        if names is None:
            self.names = [str(value) for value in values]
        else:
            if len(names) != len(values):
                raise ValueError("`names` must be the same length as `values`.")

            self.names = names

        # Icons default to `None`. Also, fetch their SVG sources so any errors
        # are raised now, rather than later.
        if icons is None:
            self.icon_svg_sources = [None] * len(values)
        else:
            if len(icons) != len(values):
                raise ValueError("`icons` must be the same length as `values`.")

            registry = icon_registry.IconRegistry.get_singleton()
            self.icon_svg_sources = [
                None if icon is None else registry.get_icon_svg(icon) for icon in icons
            ]

        self.selected_value = selected_value

    def __post_init__(self) -> None:
        # Make sure a value is selected, if needed
        if self.selected_value is None and not self.allow_none:
            self.selected_value = self.values[0]

    def _fetch_selected_name(self) -> Optional[str]:
        # None is fine
        if self.selected_value is None:
            assert self.allow_none
            return None

        # The frontend works with names, not values. Get the corresponding name.

        # Avoid hammering a potential state binding
        selected_value = self.selected_value

        # Fetch the name
        for name, value in zip(self.names, self.values):
            if value == selected_value:
                return name
        else:
            # If nothing matches, just select the first option
            return self.names[0]

    def _custom_serialize(self) -> JsonDoc:
        result = {
            "optionNames": self.names,
            "optionIcons": self.icon_svg_sources,
            "selectedName": self._fetch_selected_name(),
            "color": self.session.theme._serialize_colorset(self.color),
        }

        return result

    async def _on_message(self, msg: Any) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg

        # The frontend works with names, not values. Get the corresponding
        # value.
        selected_name = msg["name"]

        if selected_name is None:
            # Invalid names may be sent due to lag between the frontend and
            # backend. Ignore them.
            if not self.allow_none:
                return

            selected_value = None

        else:
            for name, value in zip(self.names, self.values):
                if name == selected_name:
                    selected_value = value
                    break
            else:
                # Invalid names may be sent due to lag between the frontend and
                # backend. Ignore them.
                return

        # TEMP, for debugging the switcher bar JS code
        # self._apply_delta_state_from_frontend({'selected_value': selected_value})
        self.selected_value = selected_value

        # Trigger the event
        await self.call_event_handler(
            self.on_change, SwitcherBarChangeEvent(self.selected_value)
        )

        # Refresh the session
        await self.session._refresh()


SwitcherBar._unique_id = "SwitcherBar-builtin"
