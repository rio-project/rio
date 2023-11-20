from __future__ import annotations

import asyncio
import copy
import json
from dataclasses import dataclass, field
from typing import *  # type: ignore

import aiofiles
import uniserde
from typing_extensions import dataclass_transform

from . import inspection, session

__all__ = [
    "UserSettings",
]


@dataclass
@dataclass_transform()
class UserSettings:
    """
    Base class for persistent user settings.

    When creating an app or website you'll often want to store some values so
    that you can access them the next time the user visits your app. A typical
    example are configuration values set by the user. You wouldn't want to ask
    for them every time.

    Rio makes it easy to store and retrieve such values. Create a class that
    inherits from `UserSettings`, and attach it to the `Session`. That's it! Rio
    will automatically store and retrieve the values for you.

    TODO: Give an example

    Warning! Since settings are stored on the user's device special
    considerations apply. Some countries have strict privacy laws regulating
    what you can store with/without the user's consent. Make sure you are
    familiar with the legal situation before going wild and storing everything
    you can think of.

    Warning! Since settings are stored on the user's device, you should never
    trust them to be valid. A malicious actor could modify them to intentionally
    trigger bugs in your app. Always validate the values before using them.

    Attributes:
        section_name: If provided, the settings file will contain a section with
            this name. This allows you to keep the configuration file organized.
            If `None`, the settings will be stored outside of any section.
    """

    # Any values from this class will be stored in the configuration file under
    # this section. This has to be set to a string. If empty, the values will be
    # set outside of any sections.
    section_name: ClassVar[str] = ""

    _rio_type_hints_cache_: ClassVar[Mapping[str, Any]]

    _rio_session_: Optional[session.Session] = field(default=None, init=False)
    _rio_dirty_attribute_names_: Set[str] = field(default_factory=set, init=False)
    _rio_synchronization_task_: Optional[asyncio.Task[None]] = field(
        default=None, init=False
    )

    def __init_subclass__(cls) -> None:
        dataclass(cls)
        cls._rio_type_hints_cache_ = inspection.get_type_annotations(cls)

        if cls.section_name.startswith("section:"):
            raise ValueError(f"Section names may not start with 'section:'")

    @classmethod
    def _from_json(
        cls,
        sess: session.Session,
        settings_json: Dict[str, object],
        defaults: Self,
    ) -> Self:
        # Create the instance for this attachment. Bypass the constructor so
        # the instance doesn't immediately try to synchronize with the
        # frontend.
        self = object.__new__(cls)
        settings_vars = vars(self)

        if cls.section_name:
            section = cast(
                Dict[str, object],
                settings_json.get("section:" + cls.section_name, {}),
            )
        else:
            section = settings_json

        for field_name, field_type in inspection.get_type_annotations(cls).items():
            # Skip internal fields
            if field_name in UserSettings.__annotations__:
                continue

            # Try to parse the field value
            try:
                field_value = uniserde.from_json(
                    section[field_name],
                    field_type,
                )
            except (KeyError, uniserde.SerdeError):
                field_value = copy.deepcopy(getattr(defaults, field_name))

            # Set the field value
            settings_vars[field_name] = field_value

        return self

    async def _synchronize_now(self, sess: session.Session) -> None:
        async with sess._settings_sync_lock:
            # Nothing to do
            if not self._rio_dirty_attribute_names_:
                return

            if sess.running_in_window:
                await self._synchronize_now_in_window(sess)
            else:
                await self._synchronize_now_in_browser(sess)

            self._rio_dirty_attribute_names_.clear()

    async def _synchronize_now_in_window(self, sess: session.Session) -> None:
        if self.section_name:
            section = cast(
                Dict[str, object],
                sess._settings_json.setdefault("section:" + self.section_name, {}),
            )
        else:
            section = sess._settings_json

        for name in self._rio_dirty_attribute_names_:
            section[name] = uniserde.as_json(
                getattr(self, name),
                as_type=self._rio_type_hints_cache_[name],
            )

        json_data = json.dumps(sess._settings_json, indent="\t")
        config_path = sess._get_settings_file_path()

        async with aiofiles.open(config_path, "w") as file:
            await file.write(json_data)

    async def _synchronize_now_in_browser(self, sess: session.Session) -> None:
        prefix = f"{self.section_name}:" if self.section_name else ""

        # Get the dirty attributes
        dirty_attributes = {
            f"{prefix}{name}": uniserde.as_json(
                getattr(self, name),
                as_type=self._rio_type_hints_cache_[name],
            )
            for name in self._rio_dirty_attribute_names_
        }

        # Sync them with the client
        await sess._set_user_settings(dirty_attributes)

    async def _start_synchronization_task(self) -> None:
        # Wait some time to see if more attributes are marked as dirty
        while True:
            await asyncio.sleep(0.5)

            if self._rio_session_ is not None:
                break

        # Synchronize
        try:
            await self._synchronize_now(self._rio_session_)

        # Housekeeping
        finally:
            self._rio_synchronization_task_ = None

    def __setattr__(self, name: str, value: Any) -> None:
        # This attributes doesn't exist yet during the constructor
        dct = vars(self)
        dirty_attribute_names = dct.setdefault("_rio_dirty_attribute_names_", set())
        write_back_task = dct.get("_rio_synchronization_task_")

        # Set the attribute
        dct[name] = value

        # Don't synchronize internal attributes
        if name in __class__.__annotations__:
            return

        # Mark it as dirty
        dirty_attribute_names.add(name)

        # Make sure a write back task is running
        if write_back_task is not None:
            return

        # Can't sync if there's no loop yet
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return

        dct["_rio_synchronization_task_"] = loop.create_task(
            self._start_synchronization_task(),
            name="write back user settings (attribute changed)",
        )
