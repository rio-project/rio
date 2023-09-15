import reflex as rx


async def test_rebuild_widget_with_dead_parent(create_mockapp):
    class WidgetWithState(rx.Widget):
        state: str

        def build(self) -> rx.Widget:
            return rx.Text(self.state)

    widget = WidgetWithState("Hello")
    root_widget = rx.Container(rx.Container(widget))

    async with create_mockapp(root_widget) as app:
        assert not app.dirty_widgets

        # Change the widget's state, but also remove its parent from the widget tree
        widget.state = "World"
        root_widget.child = rx.Text("Goodbye")

        await app.refresh()

        # Make sure no data for dead widgets was sent to JS
        assert app.last_updated_widgets == {root_widget, root_widget.child}
