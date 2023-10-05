import rio


async def test_refresh_with_nothing_to_do(create_mockapp):
    def build():
        return rio.Text("Hello")

    async with create_mockapp(build) as app:
        app.outgoing_messages.clear()
        await app.refresh()

        assert not app.dirty_components
        assert not app.last_updated_components


async def test_refresh_with_clean_root_component(create_mockapp):
    def build():
        text_component = rio.Text("Hello")
        return rio.Container(text_component)

    async with create_mockapp(build) as app:
        text_component = app.get_component(rio.Text)

        text_component.text = "World"
        await app.refresh()

        assert app.last_updated_components == {text_component}


async def test_rebuild_component_with_dead_parent(create_mockapp):
    class ComponentWithState(rio.Component):
        state: str

        def build(self) -> rio.Component:
            return rio.Text(self.state)

    def build() -> rio.Component:
        return rio.Container(rio.Row(ComponentWithState("Hello"), rio.ProgressCircle()))

    async with create_mockapp(build) as app:
        # Change the component's state, but also remove its parent from the component
        # tree
        component = app.get_component(ComponentWithState)
        progress_component = app.get_component(rio.ProgressCircle)
        root_component = app.get_component(rio.Container)

        component.state = "Hi"
        root_component.child = progress_component

        await app.refresh()

        # Make sure no data for dead components was sent to JS
        assert app.last_updated_components == {root_component}
