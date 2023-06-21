import reflex as rx


class Parent(rx.Widget):
    text: str = ""

    def build(self):
        return rx.Text(Parent.text)


class Grandparent(rx.Widget):
    text: str = ""

    def build(self):
        return Parent(Grandparent.text)


async def test_binding_assignment_on_child(MockApp):
    root_widget = Parent()
    app = await MockApp(root_widget)
    text_widget: rx.Text = app.get_build_output(root_widget)

    assert not app.dirty_widgets

    text_widget.text = "Hello"

    assert app.dirty_widgets == {root_widget, text_widget}
    assert root_widget.text == "Hello"
    assert text_widget.text == "Hello"


async def test_binding_assignment_on_parent(MockApp):
    root_widget = Parent()
    app = await MockApp(root_widget)
    text_widget: rx.Text = app.get_build_output(root_widget)

    assert not app.dirty_widgets

    root_widget.text = "Hello"

    assert app.dirty_widgets == {root_widget, text_widget}
    assert root_widget.text == "Hello"
    assert text_widget.text == "Hello"


async def test_binding_assignment_on_sibling(MockApp):
    class Root(rx.Widget):
        text: str = ""

        def build(self):
            return rx.Column(
                rx.Text(Root.text),
                rx.Text(Root.text),
            )

    root_widget = Root()
    app = await MockApp(root_widget)
    text1, text2 = app.get_build_output(root_widget).children

    assert not app.dirty_widgets

    text1.text = "Hello"

    assert app.dirty_widgets == {root_widget, text1, text2}
    assert root_widget.text == "Hello"
    assert text1.text == "Hello"
    assert text2.text == "Hello"


async def test_binding_assignment_on_grandchild(MockApp):
    root_widget = Grandparent()
    app = await MockApp(root_widget)
    parent: Parent = app.get_build_output(root_widget)
    text_widget: rx.Text = app.get_build_output(parent)

    assert not app.dirty_widgets

    text_widget.text = "Hello"

    assert app.dirty_widgets == {root_widget, parent, text_widget}
    assert root_widget.text == "Hello"
    assert parent.text == "Hello"
    assert text_widget.text == "Hello"


async def test_binding_assignment_on_middle(MockApp):
    root_widget = Grandparent()
    app = await MockApp(root_widget)
    parent: Parent = app.get_build_output(root_widget)
    text_widget: rx.Text = app.get_build_output(parent)

    assert not app.dirty_widgets

    parent.text = "Hello"

    assert app.dirty_widgets == {root_widget, parent, text_widget}
    assert root_widget.text == "Hello"
    assert parent.text == "Hello"
    assert text_widget.text == "Hello"


async def test_binding_assignment_on_child_after_reconciliation(MockApp):
    root_widget = Parent()
    app = await MockApp(root_widget)
    text_widget: rx.Text = app.get_build_output(root_widget)

    assert not app.dirty_widgets

    # Rebuild the parent, which reconciles the child
    await root_widget.force_refresh()

    text_widget.text = "Hello"

    assert app.dirty_widgets == {root_widget, text_widget}
    assert root_widget.text == "Hello"
    assert text_widget.text == "Hello"


async def test_binding_assignment_on_parent_after_reconciliation(MockApp):
    root_widget = Parent()
    app = await MockApp(root_widget)
    text_widget: rx.Text = app.get_build_output(root_widget)

    assert not app.dirty_widgets

    # Rebuild the parent, which reconciles the child
    await root_widget.force_refresh()

    root_widget.text = "Hello"

    assert app.dirty_widgets == {root_widget, text_widget}
    assert root_widget.text == "Hello"
    assert text_widget.text == "Hello"


async def test_binding_assignment_on_sibling_after_reconciliation(MockApp):
    class Root(rx.Widget):
        text: str = ""

        def build(self):
            return rx.Column(
                rx.Text(Root.text),
                rx.Text(Root.text),
            )

    root_widget = Root()
    app = await MockApp(root_widget)
    text1, text2 = app.get_build_output(root_widget).children

    assert not app.dirty_widgets

    # Rebuild the parent, which reconciles the children
    await root_widget.force_refresh()

    text1.text = "Hello"

    assert app.dirty_widgets == {root_widget, text1, text2}
    assert root_widget.text == "Hello"
    assert text1.text == "Hello"
    assert text2.text == "Hello"


async def test_binding_assignment_on_grandchild_after_reconciliation(MockApp):
    root_widget = Grandparent()
    app = await MockApp(root_widget)
    parent: Parent = app.get_build_output(root_widget)
    text_widget: rx.Text = app.get_build_output(parent)

    assert not app.dirty_widgets

    # Rebuild the parent, which reconciles the child
    await root_widget.force_refresh()

    text_widget.text = "Hello"

    assert app.dirty_widgets == {root_widget, parent, text_widget}
    assert root_widget.text == "Hello"
    assert parent.text == "Hello"
    assert text_widget.text == "Hello"


async def test_binding_assignment_on_middle_after_reconciliation(MockApp):
    root_widget = Grandparent()
    app = await MockApp(root_widget)
    parent: Parent = app.get_build_output(root_widget)
    text_widget: rx.Text = app.get_build_output(parent)

    assert not app.dirty_widgets

    # Rebuild the parent, which reconciles the child
    await root_widget.force_refresh()

    parent.text = "Hello"

    assert app.dirty_widgets == {root_widget, parent, text_widget}
    assert root_widget.text == "Hello"
    assert parent.text == "Hello"
    assert text_widget.text == "Hello"
