from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

import plotly.express as px

import reflex as rx
import reflex.validator
import reflex.widgets.default_design as widgets

theme = widgets.Theme.dark()

CARD_STYLE = widgets.BoxStyle(
    fill=theme.neutral_color,
    corner_radius=theme.corner_radius,
    shadow_color=theme.active_color.replace(opacity=0.1),
)

CARD_STYLE_HOVER = CARD_STYLE.replace(
    fill=theme.neutral_active_color,
    shadow_radius=2.5,
)


@dataclass
class SubConfig:
    sub_foo: int
    sub_bar: List[str]


class TestUserSettings(rx.UserSettings):
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
    search_text: str = ""

    async def _on_button_press(self, _: widgets.ButtonPressEvent) -> None:
        sett = self.session.attachments[TestUserSettings]
        sett.counter += 1
        await self.force_refresh()

    def build(self) -> rx.Widget:
        return widgets.Rectangle(
            child=widgets.Column(
                widgets.Text(
                    "Reflex UI",
                    style=widgets.TextStyle(
                        font_color=theme.main_color,
                        font_size=3.0,
                    ),
                    margin_top=1.0,
                ),
                widgets.Text(
                    "The reactive UI library for Python",
                    style=widgets.TextStyle(font_color=theme.main_color),
                    margin_top=0.6,
                ),
                widgets.TextInput(
                    placeholder="Search...",
                    text=Sidebar.search_text,
                    margin_x=1.0,
                    margin_top=4.0,
                ),
                widgets.MajorButton(
                    "Button",
                    on_press=self._on_button_press,
                    margin_x=1.0,
                    margin_top=1.0,
                    is_sensitive=bool(self.search_text),
                    color=rx.Color.BLACK if bool(self.search_text) else rx.Color.RED,
                ),
                widgets.Text(
                    str(self.session.attachments[TestUserSettings].counter),
                    margin_top=1.0,
                ),
                widgets.ProgressCircle(
                    progress=0.4,
                    margin_top=1.0,
                ),
                align_y=0,
            ),
            style=widgets.BoxStyle(
                fill=theme.neutral_color,
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
            style=widgets.BoxStyle(fill=theme.neutral_color.darker(0.1)),
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
    default_attachments=[
        theme,
        TestUserSettings(
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
    ],
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
