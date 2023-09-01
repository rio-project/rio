from __future__ import annotations

from abc import ABC, abstractmethod

from uniserde import Jsonable

# Importing this causes a hard to avoid circular import. It's currently skipped,
# because it's only needed for a type annotation.
#
# from . import app_server


class SelfSerializing(ABC):
    """
    Properties with types that inherit from `SelfSerializing` will be serialized
    when sent to the client.
    """

    @abstractmethod
    def _serialize(self, server: app_server.AppServer) -> Jsonable:  # type: ignore
        raise NotImplementedError
