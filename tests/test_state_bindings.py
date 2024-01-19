from typing import cast

from utils import create_mockapp

import rio

StateBinding = rio.component.StateBinding
StateProperty = rio.component.StateProperty


class Parent(rio.Component):
    text: str = ""

    def build(self):
        return rio.Text(Parent.text)


class Grandparent(rio.Component):
    text: str = ""

    def build(self):
        return Parent(Grandparent.text)


async def test_bindings_arent_created_too_early():
    # There was a time when state bindings were created in `Component.__init__`.
    # Make sure they're created after *all* `__init__`s have run.
    class IHaveACustomInit(rio.Component):
        text: str

        def __init__(self, *args, text: str, **kwargs):
            super().__init__(*args, **kwargs)
            self.text = text

        def build(self) -> rio.Component:
            return rio.Text(self.text)

    class Container(rio.Component):
        text: str = "hi"

        def build(self) -> rio.Component:
            return IHaveACustomInit(text=Container.text)

    async with create_mockapp(Container) as app:
        root_component = app.get_component(Container)
        child_component = app.get_component(IHaveACustomInit)

        assert child_component.text == "hi"

        root_component.text = "bye"
        assert child_component.text == "bye"


async def test_init_receives_state_properties_as_input():
    # For a while we considered initializing state bindings before calling a
    # component's `__init__` and passing the values of the bindings as arguments
    # into `__init__`. But ultimately we decided against it, because some
    # components may want to use state properties/bindings in their __init__. So
    # make sure the `__init__` actually receives a `StateProperty` as input.
    class Square(rio.Component):
        def __init__(self, size: float):
            assert isinstance(size, StateProperty), size

            super().__init__(width=size, height=size)

        def build(self) -> rio.Component:
            return rio.Text("hi", width=self.width, height=self.height)

    class Container(rio.Component):
        size: float

        def build(self) -> rio.Component:
            return Square(Container.size)

    async with create_mockapp(lambda: Container(7)):
        pass


async def test_binding_assignment_on_child():
    async with create_mockapp(Parent) as app:
        root_component = app.get_component(Parent)
        text_component = app.get_build_output(root_component, rio.Text)

        assert not app.dirty_components

        text_component.text = "Hello"

        assert app.dirty_components == {root_component, text_component}
        assert root_component.text == "Hello"
        assert text_component.text == "Hello"


async def test_binding_assignment_on_parent():
    async with create_mockapp(Parent) as app:
        root_component = app.get_component(Parent)
        text_component = app.get_build_output(root_component)

        assert not app.dirty_components

        root_component.text = "Hello"

        assert app.dirty_components == {root_component, text_component}
        assert root_component.text == "Hello"
        assert text_component.text == "Hello"


async def test_binding_assignment_on_sibling():
    class Root(rio.Component):
        text: str = ""

        def build(self):
            return rio.Column(
                rio.Text(Root.text),
                rio.Text(Root.text),
            )

    async with create_mockapp(Root) as app:
        root_component = app.get_component(Root)
        text1, text2 = cast(
            list[rio.Text], app.get_build_output(root_component, rio.Column).children
        )

        assert not app.dirty_components

        text1.text = "Hello"

        assert app.dirty_components == {root_component, text1, text2}
        assert root_component.text == "Hello"
        assert text1.text == "Hello"
        assert text2.text == "Hello"


async def test_binding_assignment_on_grandchild():
    async with create_mockapp(Grandparent) as app:
        root_component = app.get_component(Grandparent)
        parent = cast(Parent, app.get_build_output(root_component))
        text_component: rio.Text = app.get_build_output(parent)

        assert not app.dirty_components

        text_component.text = "Hello"

        assert app.dirty_components == {root_component, parent, text_component}
        assert root_component.text == "Hello"
        assert parent.text == "Hello"
        assert text_component.text == "Hello"


async def test_binding_assignment_on_middle():
    async with create_mockapp(Grandparent) as app:
        root_component = app.get_component(Grandparent)
        parent: Parent = app.get_build_output(root_component)
        text_component: rio.Text = app.get_build_output(parent)

        assert not app.dirty_components

        parent.text = "Hello"

        assert app.dirty_components == {root_component, parent, text_component}
        assert root_component.text == "Hello"
        assert parent.text == "Hello"
        assert text_component.text == "Hello"


async def test_binding_assignment_on_child_after_reconciliation():
    async with create_mockapp(Parent) as app:
        root_component = app.get_component(Parent)
        text_component: rio.Text = app.get_build_output(root_component)

        assert not app.dirty_components

        # Rebuild the root component, which reconciles the child
        await root_component.force_refresh()

        text_component.text = "Hello"

        assert app.dirty_components == {root_component, text_component}
        assert root_component.text == "Hello"
        assert text_component.text == "Hello"


async def test_binding_assignment_on_parent_after_reconciliation():
    async with create_mockapp(Parent) as app:
        root_component = app.get_component(Parent)
        text_component: rio.Text = app.get_build_output(root_component)

        assert not app.dirty_components

        # Rebuild the root component, which reconciles the child
        await root_component.force_refresh()

        root_component.text = "Hello"

        assert app.dirty_components == {root_component, text_component}
        assert root_component.text == "Hello"
        assert text_component.text == "Hello"


async def test_binding_assignment_on_sibling_after_reconciliation():
    class Root(rio.Component):
        text: str = ""

        def build(self):
            return rio.Column(
                rio.Text(Root.text),
                rio.Text(Root.text),
            )

    async with create_mockapp(Root) as app:
        root_component = app.get_component(Root)
        text1, text2 = app.get_build_output(root_component).children

        assert not app.dirty_components

        # Rebuild the root component, which reconciles the children
        await root_component.force_refresh()

        text1.text = "Hello"

        assert app.dirty_components == {root_component, text1, text2}
        assert root_component.text == "Hello"
        assert text1.text == "Hello"
        assert text2.text == "Hello"


async def test_binding_assignment_on_grandchild_after_reconciliation():
    async with create_mockapp(Grandparent) as app:
        root_component = app.get_component(Grandparent)
        parent: Parent = app.get_build_output(root_component)
        text_component: rio.Text = app.get_build_output(parent)

        assert not app.dirty_components

        # Rebuild the root component, which reconciles the child
        await root_component.force_refresh()

        text_component.text = "Hello"

        assert app.dirty_components == {root_component, parent, text_component}
        assert root_component.text == "Hello"
        assert parent.text == "Hello"
        assert text_component.text == "Hello"


async def test_binding_assignment_on_middle_after_reconciliation():
    async with create_mockapp(Grandparent) as app:
        root_component = app.get_component(Grandparent)
        parent: Parent = app.get_build_output(root_component)
        text_component: rio.Text = app.get_build_output(parent)

        assert not app.dirty_components

        # Rebuild the root component, which reconciles the child
        await root_component.force_refresh()

        parent.text = "Hello"

        assert app.dirty_components == {root_component, parent, text_component}
        assert root_component.text == "Hello"
        assert parent.text == "Hello"
        assert text_component.text == "Hello"
