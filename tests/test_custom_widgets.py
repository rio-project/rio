
import reflex as rx
from typing import List


def test_fields_with_defaults():
    class TestWidget(rx.Widget):
        foo: List[str] = rx.field(init=False, default_factory=list)
        bar: int = rx.field(init=False, default=5)


        def build(self):
            raise NotImplementedError()
        
    widget = TestWidget()
    assert widget.foo == []
    assert widget.bar == 5
