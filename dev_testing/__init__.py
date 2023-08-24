from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

import plotly.express as px

import reflex as rx
import reflex.validator
import reflex.widgets.default_design as widgets

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


@dataclass
class SubConfig:
    sub_foo: int
    sub_bar: List[str]


class UserSettings(rx.UserSettings):
    counter: int
    foo: bool
    bar: Dict[str, SubConfig]


class Card(rx.Widget):
    child: rx.Widget

    def build(self) -> rx.Widget:
        return widgets.Rectangle(
            child=widgets.Container(
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
            widgets.Column(
                widgets.Text(self.title, multiline=True),
                widgets.Text(self.description, multiline=True),
                self.child,
            )
        )


class Sidebar(rx.Widget):
    async def _on_button_press(self, _: widgets.ButtonPressedEvent) -> None:
        sett = self.session.attachments[UserSettings]
        sett.counter += 1
        await self.force_refresh()

    def build(self) -> rx.Widget:
        return widgets.Rectangle(
            child=widgets.Column(
                widgets.Text(
                    "Reflex IO",
                    style=rx.TextStyle(
                        font_color=COLOR_ACCENT,
                        font_size=3.0,
                    ),
                    margin_top=1.0,
                ),
                widgets.Text(
                    "The reactive UI library for Python",
                    style=rx.TextStyle(font_color=COLOR_ACCENT),
                    margin_top=0.6,
                ),
                widgets.TextInput(
                    placeholder="Search...",
                    margin_x=1.0,
                    margin_top=4.0,
                ),
                widgets.Button.minor(
                    "Button",
                    on_press=self._on_button_press,
                ),
                widgets.Text(str(self.session.attachments[UserSettings].counter)),
                align_y=0,
            ),
            style=rx.BoxStyle(
                fill=COLOR_FG,
            ),
        )


class WidgetShowcase(rx.Widget):
    def build(self) -> rx.Widget:
        df = px.data.gapminder().query("country=='Canada'")
        fig = px.line(df, x="year", y="lifeExp", title="Life expectancy in Canada")

        return widgets.Rectangle(
            child=widgets.Row(
                Sidebar(
                    width=30,
                ),
                ShowcaseCard(
                    "Hello Worlds",
                    "Much hello!",
                    widgets.Column(
                        widgets.Text("Hello World"),
                        widgets.Text("Hello World"),
                        widgets.Text("Hello World"),
                        widgets.Plot(
                            figure=fig,
                            height=20,
                        ),
                    ),
                    margin_x=4,
                    align_y=0.2,
                    width="grow",
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
    "Reflex Showcase",
    WidgetShowcase,
    on_session_start=lambda sess: print("Session Started"),
    on_session_end=lambda sess: print("Session Ended"),
    default_user_settings=UserSettings(
        counter=0,
        foo=True,
        bar={
            "a": SubConfig(
                sub_foo=1,
                sub_bar=["a", "b", "c"],
            ),
            "b": SubConfig(
                sub_foo=2,
                sub_bar=["d", "e", "f"],
            ),
        },
    ),
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
