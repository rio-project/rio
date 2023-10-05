import rio


async def test_refresh_with_nothing_to_do(create_mockapp):
    def build():
        return rio.Text("Hello")

    async with create_mockapp(build) as app:
        app.outgoing_messages.clear()
        await app.refresh()

        assert not app.dirty_widgets
        assert not app.last_updated_widgets


async def test_refresh_with_clean_root_widget(create_mockapp):
    def build():
        text_widget = rio.Text("Hello")
        return rio.Container(text_widget)

    async with create_mockapp(build) as app:
        text_widget = app.get_widget(rio.Text)

        text_widget.text = "World"
        await app.refresh()

        assert app.last_updated_widgets == {text_widget}


async def test_rebuild_widget_with_dead_parent(create_mockapp):
    class WidgetWithState(rio.Component):
        state: str

        def build(self) -> rio.Component:
            return rio.Text(self.state)

    def build() -> rio.Component:
        return rio.Container(rio.Row(WidgetWithState("Hello"), rio.ProgressCircle()))

    async with create_mockapp(build) as app:
        # Change the widget's state, but also remove its parent from the widget
        # tree
        widget = app.get_widget(WidgetWithState)
        progress_widget = app.get_widget(rio.ProgressCircle)
        root_widget = app.get_widget(rio.Container)

        widget.state = "Hi"
        root_widget.child = progress_widget

        await app.refresh()

        # Make sure no data for dead widgets was sent to JS
        assert app.last_updated_widgets == {root_widget}
