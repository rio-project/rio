from pathlib import Path
from typing import *  # type: ignore

import plotly.express as px

import reflex as rx

theme = rx.Theme()

CARD_STYLE = rx.BoxStyle(
    fill=theme.surface_color,
    corner_radius=theme.corner_radius,
    # shadow_color=theme.active_color.replace(opacity=0.1),
)

CARD_STYLE_HOVER = CARD_STYLE.replace(
    fill=theme.surface_active_color,
    # shadow_radius=2.5,
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


class KeyEventTester(rx.Widget):
    event: rx.KeyDownEvent = rx.KeyDownEvent("unknown", "unknown", "", frozenset())

    def on_key_down(self, event: rx.KeyDownEvent) -> None:
        self.event = event

    def build(self) -> rx.Widget:
        return rx.KeyEventListener(
            rx.Text(
                f"""Hardware key: {self.event.hardware_key}
Software key: {self.event.software_key}
Input text: {self.event.text}
Modifiers: {self.event.modifiers}"""
            ),
            on_key_down=self.on_key_down,
        )


class Sidebar(rx.Widget):
    search_text: str = ""
    expanded: bool = False

    def build(self) -> rx.Widget:
        return Card(
            child=rx.Column(
                rx.Text(
                    "Reflex UI",
                    style=rx.TextStyle(
                        font_color=theme.primary_color,
                        font_size=3.0,
                    ),
                    margin_top=1.0,
                ),
                rx.Text(
                    "The reactive UI library for Python",
                    style=rx.TextStyle(font_color=theme.primary_color),
                    margin_top=0.6,
                ),
                rx.Grid(
                    [
                        rx.TextInput(
                            placeholder="Plain",
                            text=Sidebar.search_text,
                            prefix_text="prefix",
                            on_change=lambda evt: print("plain-change:", evt.text),
                            is_sensitive=False,
                        ),
                        rx.TextInput(
                            placeholder="Secret",
                            text=Sidebar.search_text,
                            is_secret=True,
                            suffix_text="suffix",
                            on_confirm=lambda evt: print("secret-confirm:", evt.text),
                        ),
                    ],
                    [
                        rx.Button(
                            "Button",
                            # icon="bootstrap/zoom-out",
                            is_sensitive=bool(self.search_text),
                            color=rx.Color.BLACK
                            if bool(self.search_text)
                            else rx.Color.RED,
                        ),
                        rx.ProgressCircle(
                            progress=None,
                        ),
                    ],
                ),
                KeyEventTester(),
                rx.Row(
                    rx.Icon(
                        "archive",
                        fill=rx.Color.BLUE,
                    ),
                    rx.Icon(
                        "material/archive/fill",
                        fill=rx.LinearGradientFill(
                            (rx.Color.RED, 0),
                            (rx.Color.BLUE, 1),
                            angle_degrees=20,
                        ),
                    ),
                    rx.Icon(
                        "material/castle",
                        fill=rx.ImageFill(
                            Path(__file__).parent / "test.png",
                        ),
                    ),
                    height=3.0,
                ),
                rx.Slider(value=0.1),
                rx.Button(
                    "Foo",
                    on_press=lambda _: print("Button Pressed"),
                    shape="pill",
                    style="major",
                    is_loading=True,
                ),
                rx.Button(
                    "Bar",
                    icon="material/castle/fill",
                    shape="rounded",
                    style="minor",
                    color="danger",
                    # is_sensitive=False,
                ),
                rx.Button(
                    "Baz",
                    shape="rectangle",
                    color="warning",
                ),
                rx.Button(
                    "Spam",
                    shape="circle",
                    color=rx.Color.CYAN,
                    width=20,
                    height=20,
                    align_x=0.5,
                ),
                rx.ProgressBar(0.4),
                rx.ProgressBar(None),
                rx.Switch(
                    on_change=lambda _: print("Switch 1 Changed"),
                ),
                rx.Switch(
                    is_sensitive=False,
                    on_change=lambda _: print("Switch 2 Changed"),
                ),
                rx.NumberInput(
                    3.0,
                    placeholder="Number",
                    prefix_text="$",
                    decimals=2,
                ),
                rx.Text("I ❤️ U 🏎️"),
                rx.Revealer(
                    "Revealer",
                    rx.Text("Hello World"),
                    on_change=lambda evt: print("Revealer Changed:", evt.is_expanded),
                    is_expanded=Sidebar.expanded,
                ),
                rx.Switch(
                    is_on=Sidebar.expanded,
                ),
                rx.Rectangle(
                    style=rx.BoxStyle(fill=rx.Color.YELLOW),
                    ripple=True,
                    width=10,
                    height=10,
                ),
                spacing=1.0,
                align_y=0,
            ),
            margin=1.0,
        )


class WidgetShowcase(rx.Widget):
    def build(self) -> rx.Widget:
        df = px.data.gapminder().query("country=='Canada'")
        fig = px.line(
            df,
            x="year",
            y="lifeExp",
            title="Life expectancy in Canada",
        )

        return rx.Rectangle(
            child=rx.Row(
                Sidebar(
                    width=30,
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
                            # height=20,
                        ),
                    ),
                    margin_x=4,
                    align_y=0.2,
                    width="grow",
                ),
            ),
            style=rx.BoxStyle(fill=theme.surface_color),
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
    ],
)


if __name__ == "__main__":
    rx_app.run_as_web_server(
        port=8001,
        external_url="http://localhost:8001",
        quiet=False,
        _validator_factory=validator_factory,
    )
else:
    app = rx_app.as_fastapi(
        external_url="http://localhost:8001",
        _validator_factory=validator_factory,
    )
