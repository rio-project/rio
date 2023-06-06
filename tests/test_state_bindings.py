
import reflex as rx


def test_binding_makes_sibling_dirty(MockApp):
    class Root(rx.Widget):
        text: str = ""

        def build(self):
            return rx.Column([
                rx.Text(Root.text),
                rx.Text(Root.text),
            ])

    root = Root()
    app = MockApp(root)
    text1, text2 = app.get_build_output(root).children

    text1.text = "Hello"
    assert text2 in app.dirty_widgets

