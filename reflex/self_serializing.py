from abc import ABC, abstractmethod

from uniserde import Jsonable


class SelfSerializing(ABC):
    """
    Properties with types that inherit from `SelfSerializing` will be serialized
    when sent to the client.
    """

    @abstractmethod
    def _serialize(self) -> Jsonable:
        raise NotImplementedError
