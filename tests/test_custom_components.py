import dataclasses
from typing import List

import pytest
from utils import create_mockapp

import rio


def test_fields_with_defaults(enable_component_instantiation):
    class TestComponent(rio.Component):
        foo: List[str] = dataclasses.field(init=False, default_factory=list)
        bar: int = dataclasses.field(init=False, default=5)

        def build(self) -> rio.Component:
            raise NotImplementedError()

    component = TestComponent()
    assert component.foo == []
    assert component.bar == 5


async def test_init_cannot_read_state_properties():
    # Accessing state properties in `__init__` is not allowed because state
    # bindings aren't initialized yet at that point. In development mode, trying
    # to access a state property in `__init__` should raise an exception.
    class IllegalComponent(rio.Component):
        foo: int

        def __init__(self, foo: int):
            super().__init__()

            self.foo = foo

            with pytest.raises(Exception):
                _ = self.foo

            with pytest.raises(Exception):
                _ = self.margin_top

        def build(self) -> rio.Component:
            return rio.Text("hi", margin_top=self.margin_top)

    class Container(rio.Component):
        def build(self) -> rio.Component:
            return IllegalComponent(17)

    async with create_mockapp(Container):
        pass


async def test_post_init():
    class TestComponent(rio.Component):
        post_init_called: bool = False

        def __post_init__(self):
            self.post_init_called = True

        def build(self) -> rio.Component:
            return rio.Text("hi")

    async with create_mockapp(TestComponent) as app:
        root_component = app.get_component(TestComponent)
        assert root_component.post_init_called
