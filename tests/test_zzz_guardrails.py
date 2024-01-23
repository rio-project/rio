# The "zzz" in the file name is there to ensure that this file runs last, so
# that the remaining tests run without the monkeypatches applied.

import pytest
from utils import create_mockapp, enable_component_instantiation

import rio
from rio.debug.monkeypatches import apply_monkeypatches

apply_monkeypatches()


@enable_component_instantiation
def test_type_checking():
    rio.Text(
        "foo",
        key="key",
        multiline=True,
        margin_x=2,
        width="grow",
    )
    rio.Container(rio.Text("bar"))

    class Comp1(rio.Component):
        attr: list["int"]  # <- partially made of forward references

        def build(self) -> rio.Component:
            return rio.Text("")

    Comp1([1, 2, 3])


@pytest.mark.parametrize(
    "func",
    [
        lambda: rio.Text(b"foo"),  # type: ignore
    ],
)
@enable_component_instantiation
def test_type_checking_error(func):
    with pytest.raises(TypeError):
        func()


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