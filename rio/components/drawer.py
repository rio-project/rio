from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "Drawer",
    "DrawerOpenOrCloseEvent",
]


@dataclass
class DrawerOpenOrCloseEvent:
    is_open: bool


class Drawer(component_base.FundamentalComponent):
    """
    A container which slides in from the edge of the screen.

    Drawers are containers which can either be completely hidden from view, or
    be made visible by sliding in from the edge of the screen. They are commonly
    used for navigation on smaller displays.

    Drawers take two children: The `anchor` is always visible and positions the
    drawer. The `content` is located inside the drawer and is only visible when
    the drawer is open.

    Drawers have the ability to be `modal`. Modal drawers draw attention to
    themselves and prevent interaction with the anchor while open.

    Attributes:
        anchor: A component which is always visible and positions the drawer.

        content: A component which is only visible when the drawer is open.

        on_open_or_close: Triggered whenever the user opens or closes the
            drawer.

        side: The side of the screen from which the drawer slides in.

        is_modal: Whether the drawer should prevent interaction with the anchor
            while open.

        is_open: Whether the drawer is currently open.

        is_user_openable: Whether the user can open or close the drawer. If this
            is `False`, the drawer can only be opened or closed
            programmatically.
    """

    anchor: rio.Component
    content: rio.Component
    _: KW_ONLY
    on_open_or_close: rio.EventHandler[DrawerOpenOrCloseEvent] = None
    side: Literal["left", "right", "top", "bottom"] = "left"
    is_modal: bool = True
    is_open: bool = False
    is_user_openable: bool = True

    def _validate_delta_state_from_frontend(self, delta_state: JsonDoc) -> None:
        if not set(delta_state) <= {"is_open"}:
            raise AssertionError(
                f"Frontend tried to change `{type(self).__name__}` state: {delta_state}"
            )

        if "is_open" in delta_state and not self.is_user_openable:
            raise AssertionError(
                "Frontend tried to change value of `Drawer.is_open` even though `is_user_openable` is `False`"
            )

    async def _call_event_handlers_for_delta_state(self, delta_state: JsonDoc) -> None:
        # Trigger on_open_or_close event
        try:
            is_open = delta_state["is_open"]
        except KeyError:
            pass
        else:
            assert isinstance(is_open, bool), (is_open, type(is_open))
            await self.call_event_handler(
                self.on_open_or_close,
                DrawerOpenOrCloseEvent(is_open),
            )


Drawer._unique_id = "Drawer-builtin"
