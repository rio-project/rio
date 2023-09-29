import rio


async def test_fundamental_container_as_root(create_mockapp):
    def build():
        return rio.Row(rio.Text("Hello"))

    async with create_mockapp(build) as app:
        row_widget = app.get_widget(rio.Row)
        text_widget = app.get_widget(rio.Text)

        assert app.last_updated_widgets == {row_widget, text_widget}
