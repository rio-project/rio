import dataclasses
from typing import List

import reflex as rx


def test_fields_with_defaults():
    class TestWidget(rx.Widget):
        foo: List[str] = dataclasses.field(init=False, default_factory=list)
        bar: int = dataclasses.field(init=False, default=5)

        def build(self):
            raise NotImplementedError()

    widget = TestWidget()
    assert widget.foo == []
    assert widget.bar == 5
