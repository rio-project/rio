from typing import *  # type: ignore
from .. import widgets


__all__ = []


# Given a widget type, this dict contains the attribute names which contain
# children / child ids
CHILD_ATTRIBUTE_NAMES: Dict[str, Set[str]] = {
    widgets.Column._unique_id: {"children"},
    widgets.Dropdown._unique_id: set(),
    widgets.MouseEventListener._unique_id: {"child"},
    widgets.ProgressCircle._unique_id: set(),
    widgets.Rectangle._unique_id: {"child"},
    widgets.Row._unique_id: {"children"},
    widgets.Stack._unique_id: {"children"},
    widgets.Switch._unique_id: set(),
    widgets.Text._unique_id: set(),
    widgets.TextInput._unique_id: set(),
    widgets.Plot._unique_id: set(),
    "Placeholder": {"_child_"},
}
