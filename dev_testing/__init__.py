
from pathlib import Path
from typing import Literal

import reflex as rx
import reflex.validator


PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent
GENERATED_DIR = PROJECT_ROOT_DIR / "generated"


class AutoFormShowcase(rx.AutoForm):
    foo: str = ''
    bar: Literal['hello', 'world'] = 'world'


class WidgetShowcase(rx.Widget):
    def build(self):
        return rx.Row([
            rx.Column([
                # rx.Button("Click Me!"),
                rx.Dropdown({'Foo': 'foo', 'Bar': 'bar'}),
                rx.MarkdownView("**This** is *markdown*"),
                rx.ProgressCircle(),
                rx.MouseEventListener(
                    rx.Rectangle(rx.BoxStyle(fill=rx.Color.BLUE), width=10, height=2),
                    on_mouse_down=lambda event: print("Mouse Down!"),
                ),
                rx.Switch(),
                rx.TextInput(placeholder="Type here!"),
                rx.Text("Hello World!"),
            ]),
            rx.Column([
                rx.Stack([
                    rx.Rectangle(rx.BoxStyle(fill=rx.Color.RED), width=10, height=10),
                    rx.Rectangle(rx.BoxStyle(fill=rx.Color.GREEN), width=5, height=5, align_x=0.5, align_y=0.5),
                ]),
                AutoFormShowcase(),
            ]),
        ])


def validator_factory(sess: rx.Session) -> reflex.validator.Validator:
    return reflex.validator.Validator(
        sess,
        dump_directory_path=GENERATED_DIR,
    )


rx_app = rx.App(
    "Widget Showcase",
    WidgetShowcase,
    icon=Path("./dev_testing/test.png"),
)


# rx_app.run_in_window()


if __name__ == "__main__":
    rx_app.run_as_web_server(
        external_url=f"http://localhost:8000",
        quiet=False,
        _validator_factory=validator_factory,
    )
else:
    app = rx_app.as_fastapi(
        external_url=f"http://localhost:8000",
        _validator_factory=validator_factory,
    )
