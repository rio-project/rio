import rio


async def test_fundamental_container_as_root(create_mockapp):
    def build():
        return rio.Row(rio.Text("Hello"))

    async with create_mockapp(build) as app:
        row_component = app.get_component(rio.Row)
        text_component = app.get_component(rio.Text)

        assert app.last_updated_components == {row_component, text_component}
