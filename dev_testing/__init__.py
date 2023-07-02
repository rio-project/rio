from pathlib import Path
from typing import Literal

import plotly.express as px

import reflex as rx
import reflex.common
import reflex.validator

COLOR_BG = rx.Color.from_grey(0.6)
COLOR_FG = rx.Color.from_grey(1.0)
COLOR_ACCENT = rx.theme.COLOR_ACCENT

CORNER_RADIUS = rx.theme.CORNER_RADIUS


CARD_STYLE = rx.BoxStyle(
    fill=COLOR_FG,
    corner_radius=CORNER_RADIUS,
    shadow_color=rx.Color.from_rgb(0.3, 0.6, 1.0),
)

CARD_STYLE_HOVER = CARD_STYLE.replace(
    shadow_radius=3.0,
)


class Card(rx.Widget):
    child: rx.Widget

    def build(self) -> rx.Widget:
        return rx.Rectangle(
            child=rx.Container(
                self.child,
                margin=1.0,
            ),
            style=CARD_STYLE,
            hover_style=CARD_STYLE_HOVER,
            transition_time=0.2,
        )


class ShowcaseCard(rx.Widget):
    title: str
    description: str
    child: rx.Widget

    def build(self) -> rx.Widget:
        return Card(
            rx.Column(
                rx.Text(self.title, multiline=True),
                rx.Text(self.description, multiline=True),
                self.child,
            )
        )


class Sidebar(rx.Widget):
    def build(self) -> rx.Widget:
        return rx.Rectangle(
            child=rx.Column(
                rx.Text(
                    "Reflex IO",
                    style=rx.TextStyle(
                        font_color=COLOR_ACCENT,
                        font_size=3.0,
                    ),
                    margin_top=1.0,
                ),
                rx.Text(
                    "The reactive UI library for Python",
                    style=rx.TextStyle(font_color=COLOR_ACCENT),
                    margin_top=0.6,
                ),
                rx.TextInput(
                    placeholder="Search...",
                    margin_x=1.0,
                    margin_top=4.0,
                ),
                align_y=0,
                grow_y=False,
            ),
            style=rx.BoxStyle(
                fill=COLOR_FG,
            ),
        )


class WidgetShowcase(rx.Widget):
    def build(self) -> rx.Widget:
        return rx.Text(
            "Fooo",
            grow_x=False,
            align_x=0.2,
        )

        df = px.data.gapminder().query("country=='Canada'")
        fig = px.line(df, x="year", y="lifeExp", title="Life expectancy in Canada")

        return rx.Rectangle(
            child=rx.Row(
                Sidebar(
                    width=30,
                    grow_x=False,
                ),
                ShowcaseCard(
                    "Hello Worlds",
                    "Much hello!",
                    rx.Column(
                        rx.Text("Hello World"),
                        rx.Text("Hello World"),
                        rx.Text("Hello World"),
                        rx.Plot(
                            figure=fig,
                            height=20,
                        ),
                    ),
                    margin_x=4,
                    align_y=0.2,
                    grow_x=True,
                ),
            ),
            style=rx.BoxStyle(fill=COLOR_BG),
        )


def validator_factory(sess: rx.Session) -> rx.validator.Validator:  # type: ignore
    return rx.validator.Validator(  # type: ignore
        sess,
        # dump_directory_path=boe_reflex.common.GENERATED_DIR,
    )


rx_app = rx.App(
    "Web Scheduler",
    WidgetShowcase,
)


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
