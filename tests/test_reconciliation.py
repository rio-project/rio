from typing import Tuple

import rio


async def test_default_values_arent_considered_explicitly_set(create_mockapp):
    class SquareWidget(rio.Component):
        label: str

        def __init__(self, label, size=5):
            super().__init__(width=size, height=size)

            self.label = label

        def build(self):
            return rio.Text(self.label, width=self.width, height=self.height)

    class RootWidget(rio.Component):
        text: str

        def build(self):
            square_widget = SquareWidget(self.text, size=10)
            return rio.Container(square_widget)

    async with create_mockapp(lambda: RootWidget("Hello")) as app:
        root_widget = app.get_root_widget()
        square_widget = app.get_widget(SquareWidget)

        # Create a new SquareWidget with the default size. Since we aren't
        # explicitly passing a size to the constructor, reconciliation should
        # keep the old size.
        root_widget.text = "World"
        await root_widget.force_refresh()

        assert square_widget.label == "World"
        assert square_widget.width == 10
        assert square_widget.height == 10


async def test_reconcile_same_widget_instance(create_mockapp):
    def build():
        return rio.Container(rio.Text("Hello"))

    async with create_mockapp(build) as app:
        app.outgoing_messages.clear()

        root_widget = app.get_widget(rio.Container)
        await root_widget.force_refresh()

        # Nothing changed, so there's no need to send any data to JS. But in
        # order to know that nothing changed, the framework would have to track
        # every individual attribute of every widget. Since we forced the
        # root_widget to refresh, it's reasonable to send that widget's data to
        # JS.
        assert not app.outgoing_messages or app.last_updated_widgets == {root_widget}


async def test_reconcile_not_dirty_high_level_widget(create_mockapp):
    # Situation:
    # HighLevelWidget1 contains HighLevelWidget2
    # HighLevelWidget2 contains LowLevelContainer
    # HighLevelWidget1 is rebuilt and changes the child of LowLevelContainer
    # -> LowLevelContainer is reconciled and dirty (because it has new children)
    # -> HighLevelWidget2 is reconciled but *not* dirty because its child was
    # reconciled
    # The end result is that there is a new widget (the child of
    # LowLevelContainer), whose builder (HighLevelWidget2) is not "dirty". Make
    # sure the new widget is initialized correctly despite this.
    class HighLevelWidget1(rio.Component):
        switch: bool = False

        def build(self):
            if self.switch:
                child = rio.Switch()
            else:
                child = rio.Text("hi")

            return HighLevelWidget2(rio.Column(child))

    class HighLevelWidget2(rio.Component):
        child: rio.Component

        def build(self):
            return self.child

    async with create_mockapp(HighLevelWidget1) as app:
        root_widget = app.get_widget(HighLevelWidget1)
        root_widget.switch = True
        await app.refresh()

        assert any(
            isinstance(widget, rio.Switch) for widget in app.last_updated_widgets
        )


async def test_reconcile_unusual_types(create_mockapp):
    class Container(rio.Component):
        def build(self) -> rio.Component:
            return CustomWidget(
                integer=4,
                text="bar",
                tuple=(2.0, rio.Text("baz")),
                byte_array=bytearray(b"foo"),
            )

    class CustomWidget(rio.Component):
        integer: int
        text: str
        tuple: Tuple[float, rio.Component]
        byte_array: bytearray

        def build(self):
            return rio.Text(self.text)

    async with create_mockapp(Container) as app:
        root_widget = app.get_widget(Container)

        # As long as this doesn't crash, it's fine
        await root_widget.force_refresh()
