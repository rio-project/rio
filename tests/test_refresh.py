import rio


async def test_refresh_with_nothing_to_do(create_mockapp):
    root_widget = rio.Text("Hello")

    async with create_mockapp(root_widget) as app:
        app.outgoing_messages.clear()
        await app.refresh()

        assert not app.dirty_widgets
        assert not app.last_updated_widgets


async def test_refresh_with_clean_root_widget(create_mockapp):
    text_widget = rio.Text("Hello")
    root_widget = rio.Container(text_widget)

    async with create_mockapp(root_widget) as app:
        text_widget.text = "World"

        await app.refresh()

        assert app.last_updated_widgets == {text_widget}


async def test_rebuild_widget_with_dead_parent(create_mockapp):
    class WidgetWithState(rio.Widget):
        state: str

        def build(self) -> rio.Widget:
            return rio.Text(self.state)

    widget = WidgetWithState("Hello")
    root_widget = rio.Container(rio.Container(widget))

    async with create_mockapp(root_widget) as app:
        assert not app.dirty_widgets

        # Change the widget's state, but also remove its parent from the widget tree
        widget.state = "World"
        root_widget.child = rio.Text("Goodbye")

        await app.refresh()

        # Make sure no data for dead widgets was sent to JS
        assert app.last_updated_widgets == {root_widget, root_widget.child}
