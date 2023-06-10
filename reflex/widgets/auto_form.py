
from __future__ import annotations

from typing import Mapping, Union, Iterable, List
from typing_extensions import Self

import reflex as rx

from . import widget_base

__all__ = ["AutoForm"]


class AutoForm(widget_base.Widget):
    # actions: Union[Mapping[str, rx.EventHandler[Self]], Iterable[rx.EventHandler[Self]]]

    def build(self):
        children: List[rx.Widget] = [
            row_for_property(prop)
            for prop in self._state_properties_ - widget_base.Widget._state_properties_
        ]

        # for label, callback in self.actions.items():
        #     children.append(rx.Button(label, on_click=callback))

        return rx.Column(children)


def row_for_property(prop: widget_base.StateProperty):
    label = prop.name.replace("_", " ").title()

    widget = rx.TextInput()

    return rx.Row([rx.Text(label), widget])
