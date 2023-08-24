import json
from typing import *  # type: ignore

# Given a widget type, this dict contains the attribute names which contain
# children / child ids
CHILD_ATTRIBUTE_NAMES: Dict[str, Set[str]] = {
    "Column-builtin": {"children"},
    "Dropdown-builtin": set(),
    "MouseEventListener-builtin": {"child"},
    "ProgressCircle-builtin": set(),
    "Rectangle-builtin": {"child"},
    "Row-builtin": {"children"},
    "Stack-builtin": {"children"},
    "Switch-builtin": set(),
    "Text-builtin": set(),
    "TextInput-builtin": set(),
    "Plot-builtin": set(),
    "Placeholder": {"_child_"},
}


CHILD_ATTRIBUTE_NAMES_JSON = json.dumps(
    {
        unique_id: list(attribute_names)
        for unique_id, attribute_names in CHILD_ATTRIBUTE_NAMES.items()
    }
)
