from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from uniserde import Jsonable

# Only import `session` if type checking. This is to avoid a circular import.
if TYPE_CHECKING:
    from . import session


__all__ = ["SelfSerializing"]


class SelfSerializing(ABC):
    """
    Properties with types that inherit from `SelfSerializing` will be serialized
    when sent to the client.
    """

    @abstractmethod
    def _serialize(self, sess: session.Session) -> Jsonable:
        raise NotImplementedError
