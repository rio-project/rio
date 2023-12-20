from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "Revealer",
    "RevealerChangeEvent",
]

T = TypeVar("T")


@dataclass
class RevealerChangeEvent:
    is_expanded: bool


class Revealer(component_base.FundamentalComponent):
    header: Optional[str]
    content: component_base.Component
    _: KW_ONLY
    is_expanded: bool = False
    on_change: rio.EventHandler[RevealerChangeEvent] = None

    async def _on_state_update(self, delta_state: JsonDoc) -> None:
        if not set(delta_state) <= {"is_expanded"}:
            raise AssertionError(
                f"Frontend tried to change `{type(self).__name__}` state: {delta_state}"
            )

        # Trigger on_change event
        try:
            new_value = delta_state["is_expanded"]
        except KeyError:
            pass
        else:
            assert isinstance(new_value, bool), new_value

            if self.header is None:
                raise AssertionError(
                    f"Frontend tried to set `Revealer.is_expanded` even though it has no `header`"
                )

            await self.call_event_handler(
                self.on_change,
                RevealerChangeEvent(new_value),
            )

        self._apply_delta_state_from_frontend(delta_state)


Revealer._unique_id = "Revealer-builtin"
