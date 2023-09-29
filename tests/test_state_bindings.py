import rio

StateBinding = rio.widget_base.StateBinding
StateProperty = rio.widget_base.StateProperty


class Parent(rio.Widget):
    text: str = ""

    def build(self):
        return rio.Text(Parent.text)


class Grandparent(rio.Widget):
    text: str = ""

    def build(self):
        return Parent(Grandparent.text)


async def test_bindings_arent_created_too_early(create_mockapp):
    # There was a time when state bindings were created in `Widget.__init__`.
    # Make sure they're created after *all* `__init__`s have run.
    class IHaveACustomInit(rio.Widget):
        text: str

        def __init__(self, *args, text: str, **kwargs):
            super().__init__(*args, **kwargs)
            self.text = text

        def build(self) -> rio.Widget:
            return rio.Text(self.text)

    class Container(rio.Widget):
        text: str = "hi"

        def build(self) -> rio.Widget:
            return IHaveACustomInit(text=Container.text)

    async with create_mockapp(Container) as app:
        root_widget = app.get_widget(Container)
        child_widget = app.get_widget(IHaveACustomInit)

        assert child_widget.text == "hi"

        root_widget.text = "bye"
        assert child_widget.text == "bye"


async def test_init_receives_state_properties_as_input(create_mockapp):
    # For a while we considered initializing state bindings before calling a
    # widget's `__init__` and passing the values of the bindings as arguments
    # into `__init__`. But ultimately we decided against it, because some
    # widgets may want to use state properties/bindings in their __init__. So
    # make sure the `__init__` actually receives a `StateProperty` as input.
    class Square(rio.Widget):
        def __init__(self, size: float):
            assert isinstance(size, StateProperty), size

            super().__init__(width=size, height=size)

        def build(self) -> rio.Widget:
            return rio.Text("hi", width=self.width, height=self.height)

    class Container(rio.Widget):
        size: float

        def build(self) -> rio.Widget:
            return Square(Container.size)

    async with create_mockapp(lambda: Container(7)):
        pass


async def test_binding_assignment_on_child(create_mockapp):
    async with create_mockapp(Parent) as app:
        root_widget = app.get_root_widget()
        text_widget: rio.Text = app.get_build_output(root_widget)

        assert not app.dirty_widgets

        text_widget.text = "Hello"

        assert app.dirty_widgets == {root_widget, text_widget}
        assert root_widget.text == "Hello"
        assert text_widget.text == "Hello"


async def test_binding_assignment_on_parent(create_mockapp):
    async with create_mockapp(Parent) as app:
        root_widget = app.get_widget(Parent)
        text_widget = app.get_build_output(root_widget)

        assert not app.dirty_widgets

        root_widget.text = "Hello"

        assert app.dirty_widgets == {root_widget, text_widget}
        assert root_widget.text == "Hello"
        assert text_widget.text == "Hello"


async def test_binding_assignment_on_sibling(create_mockapp):
    class Root(rio.Widget):
        text: str = ""

        def build(self):
            return rio.Column(
                rio.Text(Root.text),
                rio.Text(Root.text),
            )

    async with create_mockapp(Root) as app:
        root_widget = app.get_root_widget()
        text1, text2 = app.get_build_output(root_widget).children

        assert not app.dirty_widgets

        text1.text = "Hello"

        assert app.dirty_widgets == {root_widget, text1, text2}
        assert root_widget.text == "Hello"
        assert text1.text == "Hello"
        assert text2.text == "Hello"


async def test_binding_assignment_on_grandchild(create_mockapp):
    async with create_mockapp(Grandparent) as app:
        root_widget = app.get_root_widget()
        parent: Parent = app.get_build_output(root_widget)
        text_widget: rio.Text = app.get_build_output(parent)

        assert not app.dirty_widgets

        text_widget.text = "Hello"

        assert app.dirty_widgets == {root_widget, parent, text_widget}
        assert root_widget.text == "Hello"
        assert parent.text == "Hello"
        assert text_widget.text == "Hello"


async def test_binding_assignment_on_middle(create_mockapp):
    async with create_mockapp(Grandparent) as app:
        root_widget = app.get_root_widget()
        parent: Parent = app.get_build_output(root_widget)
        text_widget: rio.Text = app.get_build_output(parent)

        assert not app.dirty_widgets

        parent.text = "Hello"

        assert app.dirty_widgets == {root_widget, parent, text_widget}
        assert root_widget.text == "Hello"
        assert parent.text == "Hello"
        assert text_widget.text == "Hello"


async def test_binding_assignment_on_child_after_reconciliation(create_mockapp):
    async with create_mockapp(Parent) as app:
        root_widget = app.get_root_widget()
        text_widget: rio.Text = app.get_build_output(root_widget)

        assert not app.dirty_widgets

        # Rebuild the root widget, which reconciles the child
        await root_widget.force_refresh()

        text_widget.text = "Hello"

        assert app.dirty_widgets == {root_widget, text_widget}
        assert root_widget.text == "Hello"
        assert text_widget.text == "Hello"


async def test_binding_assignment_on_parent_after_reconciliation(create_mockapp):
    async with create_mockapp(Parent) as app:
        root_widget = app.get_root_widget()
        text_widget: rio.Text = app.get_build_output(root_widget)

        assert not app.dirty_widgets

        # Rebuild the root widget, which reconciles the child
        await root_widget.force_refresh()

        root_widget.text = "Hello"

        assert app.dirty_widgets == {root_widget, text_widget}
        assert root_widget.text == "Hello"
        assert text_widget.text == "Hello"


async def test_binding_assignment_on_sibling_after_reconciliation(create_mockapp):
    class Root(rio.Widget):
        text: str = ""

        def build(self):
            return rio.Column(
                rio.Text(Root.text),
                rio.Text(Root.text),
            )

    async with create_mockapp(Root) as app:
        root_widget = app.get_root_widget()
        text1, text2 = app.get_build_output(root_widget).children

        assert not app.dirty_widgets

        # Rebuild the root widget, which reconciles the children
        await root_widget.force_refresh()

        text1.text = "Hello"

        assert app.dirty_widgets == {root_widget, text1, text2}
        assert root_widget.text == "Hello"
        assert text1.text == "Hello"
        assert text2.text == "Hello"


async def test_binding_assignment_on_grandchild_after_reconciliation(create_mockapp):
    async with create_mockapp(Grandparent) as app:
        root_widget = app.get_root_widget()
        parent: Parent = app.get_build_output(root_widget)
        text_widget: rio.Text = app.get_build_output(parent)

        assert not app.dirty_widgets

        # Rebuild the root widget, which reconciles the child
        await root_widget.force_refresh()

        text_widget.text = "Hello"

        assert app.dirty_widgets == {root_widget, parent, text_widget}
        assert root_widget.text == "Hello"
        assert parent.text == "Hello"
        assert text_widget.text == "Hello"


async def test_binding_assignment_on_middle_after_reconciliation(create_mockapp):
    async with create_mockapp(Grandparent) as app:
        root_widget = app.get_root_widget()
        parent: Parent = app.get_build_output(root_widget)
        text_widget: rio.Text = app.get_build_output(parent)

        assert not app.dirty_widgets

        # Rebuild the root widget, which reconciles the child
        await root_widget.force_refresh()

        parent.text = "Hello"

        assert app.dirty_widgets == {root_widget, parent, text_widget}
        assert root_widget.text == "Hello"
        assert parent.text == "Hello"
        assert text_widget.text == "Hello"
