import reflex as rx


async def test_default_values_arent_considered_explicitly_set(MockApp):
    class SquareWidget(rx.Widget):
        label: str

        def __init__(self, label, size=5):
            super().__init__(width=size, height=size)
            self.label = label

        def build(self):
            return rx.Text(self.label, width=self.width, height=self.height)

    square_widget = SquareWidget("Hello", size=10)
    root_widget = rx.Container(square_widget)
    app = await MockApp(root_widget)

    assert not app.dirty_widgets

    # Create a new SquareWidget with the default size. Since we aren't
    # explicitly passing a size to the constructor, reconciliation should keep
    # the old size.
    root_widget.child = SquareWidget("World")
    await root_widget.force_refresh()

    assert square_widget.label == "World"
    assert square_widget.width == 10
    assert square_widget.height == 10
