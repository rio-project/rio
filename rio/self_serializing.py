from __future__ import annotations

from abc import ABC, abstractmethod

from uniserde import Jsonable

import rio

__all__ = ["SelfSerializing"]


class SelfSerializing(ABC):
    """
    Properties with types that inherit from `SelfSerializing` will be serialized
    when sent to the client.
    """

    @abstractmethod
    def _serialize(self, sess: rio.Session) -> Jsonable:
        raise NotImplementedError
