import rio


async def test_fundamental_container_as_root(create_mockapp):
    text_widget = rio.Text("Hello")
    root_widget = rio.Row(text_widget)

    async with create_mockapp(root_widget) as app:
        assert app.last_updated_widgets == {root_widget, text_widget}
