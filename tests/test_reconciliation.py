from typing import Tuple

import rio


async def test_default_values_arent_considered_explicitly_set(create_mockapp):
    class SquareComponent(rio.Component):
        label: str

        def __init__(self, label, size=5):
            super().__init__(width=size, height=size)

            self.label = label

        def build(self):
            return rio.Text(self.label, width=self.width, height=self.height)

    class RootComponent(rio.Component):
        text: str

        def build(self):
            square_component = SquareComponent(self.text, size=10)
            return rio.Container(square_component)

    async with create_mockapp(lambda: RootComponent("Hello")) as app:
        root_component = app.get_root_component()
        square_component = app.get_component(SquareComponent)

        # Create a new SquareComponent with the default size. Since we aren't
        # explicitly passing a size to the constructor, reconciliation should
        # keep the old size.
        root_component.text = "World"
        await root_component.force_refresh()

        assert square_component.label == "World"
        assert square_component.width == 10
        assert square_component.height == 10


async def test_reconcile_same_component_instance(create_mockapp):
    def build():
        return rio.Container(rio.Text("Hello"))

    async with create_mockapp(build) as app:
        app.outgoing_messages.clear()

        root_component = app.get_component(rio.Container)
        await root_component.force_refresh()

        # Nothing changed, so there's no need to send any data to JS. But in
        # order to know that nothing changed, the framework would have to track
        # every individual attribute of every component. Since we forced the
        # root_component to refresh, it's reasonable to send that component's data to
        # JS.
        assert not app.outgoing_messages or app.last_updated_components == {
            root_component
        }


async def test_reconcile_not_dirty_high_level_component(create_mockapp):
    # Situation:
    # HighLevelComponent1 contains HighLevelComponent2
    # HighLevelComponent2 contains LowLevelContainer
    # HighLevelComponent1 is rebuilt and changes the child of LowLevelContainer
    # -> LowLevelContainer is reconciled and dirty (because it has new children)
    # -> HighLevelComponent2 is reconciled but *not* dirty because its child was
    # reconciled
    # The end result is that there is a new component (the child of
    # LowLevelContainer), whose builder (HighLevelComponent2) is not "dirty". Make
    # sure the new component is initialized correctly despite this.
    class HighLevelComponent1(rio.Component):
        switch: bool = False

        def build(self):
            if self.switch:
                child = rio.Switch()
            else:
                child = rio.Text("hi")

            return HighLevelComponent2(rio.Column(child))

    class HighLevelComponent2(rio.Component):
        child: rio.Component

        def build(self):
            return self.child

    async with create_mockapp(HighLevelComponent1) as app:
        root_component = app.get_component(HighLevelComponent1)
        root_component.switch = True
        await app.refresh()

        assert any(
            isinstance(component, rio.Switch)
            for component in app.last_updated_components
        )


async def test_reconcile_unusual_types(create_mockapp):
    class Container(rio.Component):
        def build(self) -> rio.Component:
            return CustomComponent(
                integer=4,
                text="bar",
                tuple=(2.0, rio.Text("baz")),
                byte_array=bytearray(b"foo"),
            )

    class CustomComponent(rio.Component):
        integer: int
        text: str
        tuple: Tuple[float, rio.Component]
        byte_array: bytearray

        def build(self):
            return rio.Text(self.text)

    async with create_mockapp(Container) as app:
        root_component = app.get_component(Container)

        # As long as this doesn't crash, it's fine
        await root_component.force_refresh()
