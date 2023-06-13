from pathlib import Path
from typing import Literal
import reflex.common

import reflex as rx
import reflex.validator
import plotly.express as px


PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent
GENERATED_DIR = PROJECT_ROOT_DIR / "generated"


# class AutoFormShowcase(rx.AutoForm):
#     foo: str = ''
#     bar: Literal['hello', 'world'] = 'world'


class WidgetShowcase(rx.Widget):
    def build(self):
        df = px.data.gapminder().query("country=='Canada'")
        fig = px.line(df, x="year", y="lifeExp", title="Life expectancy in Canada")

        fig.write_html(
            reflex.common.PACKAGE_ROOT_DIR / "plot.html",
            full_html=True,
            include_plotlyjs="cdn",
            default_width="100%",
            default_height="100%",
            validate=True,
        )

        return rx.Plot(fig)


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
