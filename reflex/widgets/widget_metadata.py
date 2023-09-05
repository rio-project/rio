import json
from typing import *  # type: ignore

# Given a widget type, this dict contains the attribute names which contain
# children / child ids
CHILD_ATTRIBUTE_NAMES: Dict[str, Set[str]] = {
    "Button-builtin": {"child"},
    "Column-builtin": {"children"},
    "Dropdown-builtin": set(),
    "Grid-builtin": {'_children'},
    "Icon-builtin": set(),
    "KeyEventListener-builtin": {"child"},
    "MediaPlayer-builtin": set(),
    "MouseEventListener-builtin": {"child"},
    "Placeholder": {"_child_"},
    "Plot-builtin": set(),
    "ProgressBar-builtin": set(),
    "ProgressCircle-builtin": set(),
    "Rectangle-builtin": {"child"},
    "Row-builtin": {"children"},
    "Slider-builtin": set(),
    "Stack-builtin": {"children"},
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
