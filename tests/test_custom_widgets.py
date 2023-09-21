import dataclasses
from typing import List

import pytest

import rio as rx

# @pytest.fixture(autouse=True)
# def _enable_widget_instantiation(enable_widget_instantiation):
#     pass


def test_fields_with_defaults(enable_widget_instantiation):
    class TestWidget(rx.Widget):
        foo: List[str] = dataclasses.field(init=False, default_factory=list)
        bar: int = dataclasses.field(init=False, default=5)

        def build(self):
            raise NotImplementedError()

    widget = TestWidget()
    assert widget.foo == []
    assert widget.bar == 5


async def test_init_cannot_read_state_properties(create_mockapp):
    # Accessing state properties in `__init__` is not allowed because state
    # bindings aren't initialized yet at that point. In development mode, trying
    # to access a state property in `__init__` should raise an exception.
    class IllegalWidget(rx.Widget):
        foo: int

        def __init__(self, foo: int):
            super().__init__()

            self.foo = foo

            with pytest.raises(Exception):
                _ = self.foo

            with pytest.raises(Exception):
                _ = self.margin_top

        def build(self) -> rx.Widget:
            return rx.Text("hi", margin_top=self.margin_top)

    class Container(rx.Widget):
        def build(self) -> rx.Widget:
            return IllegalWidget(17)

    root_widget = Container()
    async with create_mockapp(root_widget):
        pass
