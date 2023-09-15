from __future__ import annotations

from typing import *  # type: ignore

import reflex as rx

__all__ = [
    "currently_building_widget",
]


# Before a widget is built, this value is set to that widget. This allows newly
# created widgets to infer their creator, as well as session.
#
# - `Widget`: The widget that is currently being built
# - `None`: The app's build method is currently being called
currently_building_widget: Optional[rx.Widget] = None


# Same as `currently_building_widget`, but holding that widget's session.
#
# - `Session`: The session that owns the currently building widget
# - `None`: No build is currently in progress
currently_building_session: Optional[rx.Session] = None
