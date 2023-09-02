import json
from typing import *  # type: ignore

# Given a widget type, this dict contains the attribute names which contain
# children / child ids
CHILD_ATTRIBUTE_NAMES: Dict[str, Set[str]] = {
    "Button-builtin": {"child"},
    "Column-builtin": {"children"},
    "Dropdown-builtin": set(),
    "Icon-builtin": set(),
    "MouseEventListener-builtin": {"child"},
    "Placeholder": {"_child_"},
    "Plot-builtin": set(),
    "ProgressCircle-builtin": set(),
    "Rectangle-builtin": {"child"},
    "Row-builtin": {"children"},
    "Stack-builtin": {"children"},
    "Slider-builtin": set(),
    "Switch-builtin": set(),
    "Text-builtin": set(),
    "TextInput-builtin": set(),
}


CHILD_ATTRIBUTE_NAMES_JSON = json.dumps(
    {
        unique_id: list(attribute_names)
        for unique_id, attribute_names in CHILD_ATTRIBUTE_NAMES.items()
    }
)
