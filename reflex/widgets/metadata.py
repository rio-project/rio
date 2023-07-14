from typing import *  # type: ignore

from .column import Column
from .dropdown import Dropdown
from .mouse_event_listener import MouseEventListener
from .plot import Plot
from .progress_circle import ProgressCircle
from .rectangle import Rectangle
from .row import Row
from .stack import Stack
from .switch import Switch
from .text import Text
from .text_input import TextInput

# Given a widget type, this dict contains the attribute names which contain
# children / child ids
CHILD_ATTRIBUTE_NAMES: Dict[str, Set[str]] = {
    Column._unique_id: {"children"},
    Dropdown._unique_id: set(),
    MouseEventListener._unique_id: {"child"},
    ProgressCircle._unique_id: set(),
    Rectangle._unique_id: {"child"},
    Row._unique_id: {"children"},
    Stack._unique_id: {"children"},
    Switch._unique_id: set(),
    Text._unique_id: set(),
    TextInput._unique_id: set(),
    Plot._unique_id: set(),
    "Placeholder": {"_child_"},
}
