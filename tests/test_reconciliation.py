from typing import Tuple

import rio


async def test_default_values_arent_considered_explicitly_set(create_mockapp):
    class SquareWidget(rio.Widget):
        label: str

        def __init__(self, label, size=5):
            super().__init__(width=size, height=size)

            self.label = label

        def build(self):
            return rio.Text(self.label, width=self.width, height=self.height)

    square_widget = SquareWidget("Hello", size=10)
    root_widget = rio.Container(square_widget)

    async with create_mockapp(root_widget) as app:
        assert not app.dirty_widgets

        # Create a new SquareWidget with the default size. Since we aren't
        # explicitly passing a size to the constructor, reconciliation should keep
        # the old size.
        root_widget.child = SquareWidget("World")
        await root_widget.force_refresh()

        assert square_widget.label == "World"
        assert square_widget.width == 10
        assert square_widget.height == 10


async def test_reconcile_same_widget_instance(create_mockapp):
    root_widget = rio.Container(rio.Text("Hello"))

    async with create_mockapp(root_widget) as app:
        app.outgoing_messages.clear()

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
    class HighLevelWidget1(rio.Widget):
        switch: bool = False

        def build(self):
            if self.switch:
                child = rio.Switch()
            else:
                child = rio.Text("hi")

            return HighLevelWidget2(rio.Column(child))

    class HighLevelWidget2(rio.Widget):
        child: rio.Widget

        def build(self):
            return self.child

    root_widget = HighLevelWidget1()

    async with create_mockapp(root_widget) as app:
        root_widget.switch = True
        await app.refresh()

        assert any(
            isinstance(widget, rio.Switch) for widget in app.last_updated_widgets
        )


async def test_reconcile_unusual_types(create_mockapp):
    class Container(rio.Widget):
        def build(self) -> rio.Widget:
            return CustomWidget(
                integer=4,
                text="bar",
                tuple=(2.0, rio.Text("baz")),
                byte_array=bytearray(b"foo"),
            )

    class CustomWidget(rio.Widget):
        integer: int
        text: str
        tuple: Tuple[float, rio.Widget]
        byte_array: bytearray

        def build(self):
            return rio.Text(self.text)

    root_widget = Container()
    async with create_mockapp(root_widget) as mock_app:
        await root_widget.force_refresh()
