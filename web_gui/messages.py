import uniserde
from dataclasses import dataclass
from .common import Jsonable
from typing import Any


@uniserde.as_child
class SocketMessage(uniserde.Serde):
    """
    Base class for socket messages.
    """


@dataclass
class ReplaceWidgets(SocketMessage):
    """
    Replace all widgets in the UI with the given one.
    """

    widget: Any
