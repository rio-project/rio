from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import *  # type: ignore

import uniserde
from typing_extensions import dataclass_transform

from . import session

__all__ = [
    "UserSettings",
]


@dataclass
@dataclass_transform()
class UserSettings:
    # Any values from this class will be stored in the configuration file under
    # this section. This has to be set to a string. If empty, the values will be
    # set outside of any sections.
    section_name: ClassVar[str] = ""

    _reflex_session_: Optional[session.Session] = field(default=None, init=False)
    _reflex_dirty_attribute_names_: Set[str] = field(default_factory=set, init=False)
    _reflex_synchronization_task_: Optional[asyncio.Task] = field(
        default=None, init=False
    )
    _reflex_type_hints_cache_: ClassVar[Dict[str, Any]]

    def __init_subclass__(cls) -> None:
        dataclass(cls)
        cls._reflex_type_hints_cache_ = get_type_hints(cls)

    async def _synchronize_now(self, sess: session.Session) -> None:
        prefix = f"{self.section_name}:" if self.section_name else ""

        async with sess._settings_sync_lock:
            # Get the dirty attributes
            dirty_attributes = {
                f"{prefix}{name}": uniserde.as_json(
                    getattr(self, name),
                    as_type=self._reflex_type_hints_cache_[name],
                )
                for name in self._reflex_dirty_attribute_names_
            }
            self._reflex_dirty_attribute_names_.clear()

            # Nothing to do
            if not dirty_attributes:
                return

            # Sync them with the client
            await sess._set_user_settings(dirty_attributes)

    async def _start_synchronization_task(self) -> None:
        # Wait some time to see if more attributes are marked as dirty
        while True:
            await asyncio.sleep(0.5)

            if self._reflex_session_ is not None:
                break

        # Synchronize
        try:
            await self._synchronize_now(self._reflex_session_)

        # Housekeeping
        finally:
            self._reflex_synchronization_task_ = None

    def __setattr__(self, name: str, value: Any) -> None:
        # This attributes doesn't exist yet during the constructor
        dct = vars(self)
        dirty_attribute_names = dct.setdefault("_reflex_dirty_attribute_names_", set())
        write_back_task = dct.get(
            "_reflex_synchronization_task_",
        )

        # Set the attribute
        dct[name] = value

        # Don't synchronize internal attributes
        if name in __class__.__annotations__:
            return

        # Mark it as dirty
        dirty_attribute_names.add(name)

        # Can't sync if there's no loop yet
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return

        # Make sure a write back task is running
        if write_back_task is None:
            dct["_reflex_synchronization_task_"] = loop.create_task(
                self._start_synchronization_task(),
                name="write back user settings (attribute changed)",
            )