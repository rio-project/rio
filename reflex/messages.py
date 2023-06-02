from dataclasses import dataclass
from typing import *  # type: ignore

import uniserde


@uniserde.as_child
class OutgoingMessage(uniserde.Serde):
    """
    Base class for socket messages.
    """


@dataclass
class UpdateWidgetStates(OutgoingMessage):
    """
    Replace all widgets in the UI with the given one.
    """

    # Maps widget ids to serialized widgets. The widgets may be partial, i.e.
    # any property may be missing.
    delta_states: Dict[int, Any]

    # Tells the client to make the given widget the new root widget.
    root_widget_id: Optional[int]


@dataclass
class EvaluateJavascript(OutgoingMessage):
    """
    Evaluate the given javascript code in the client.
    """

    javascript_source: str


@dataclass
class RequestFileUpload(OutgoingMessage):
    """
    Tell the client to upload a file to the server.
    """

    upload_url: str
    file_extensions: Optional[List[str]]
    multiple: bool


@uniserde.as_child
class IncomingMessage(uniserde.Serde):
    """
    Base class for socket messages.
    """


@dataclass
class WidgetStateUpdate(IncomingMessage):
    widget_id: int
    delta_state: Any


@dataclass
class WidgetMessage(IncomingMessage):
    widget_id: int
    payload: Any
