from __future__ import annotations

from abc import ABC, abstractmethod
from typing import *  # type: ignore

from uniserde import Jsonable

# Only import `app_server` if type checking. This is to avoid a circular import.
if TYPE_CHECKING:
    from . import app_server


__all__ = [
    "SelfSerializing",
]


class SelfSerializing(ABC):
    """
    Properties with types that inherit from `SelfSerializing` will be serialized
    when sent to the client.
    """

    @abstractmethod
    def _serialize(self, server: app_server.AppServer) -> Jsonable:  # type: ignore
        raise NotImplementedError
