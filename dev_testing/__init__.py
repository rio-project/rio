from dataclasses import dataclass
from typing import *  # type: ignore

import plotly.express as px

# import bootstrap_icons
import reflex as rx

theme = rx.Theme.dark()

CARD_STYLE = rx.BoxStyle(
    fill=theme.neutral_color,
    corner_radius=theme.corner_radius,
    # shadow_color=theme.active_color.replace(opacity=0.1),
)

CARD_STYLE_HOVER = CARD_STYLE.replace(
    fill=theme.neutral_active_color,
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


class Sidebar(rx.Widget):
    search_text: str = ""

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
                rx.TextInput(
                    placeholder="Search...",
                    text=Sidebar.search_text,
                    margin_x=1.0,
                    margin_top=4.0,
                ),
                rx.MajorButton(
                    "Button",
                    # icon="bootstrap/zoom-out",
                    margin_x=1.0,
                    margin_top=1.0,
                    is_sensitive=bool(self.search_text),
                    color=rx.Color.BLACK if bool(self.search_text) else rx.Color.RED,
                ),
                rx.ProgressCircle(
                    progress=None,
                    margin_top=1.0,
                ),
                # rx.Icon(
                #     # "reflex/circle",
                #     "bootstrap/zoom-out",
                #     # fill=rx.Color.RED,
                #     # fill=rx.LinearGradientFill(
                #     #     (rx.Color.RED, 0),
                #     #     (rx.Color.BLUE, 1),
                #     #     angle_degrees=20,
                #     # ),
                #     fill=rx.ImageFill(
                #         "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.startupsos.com%2Fwp-content%2Fuploads%2F2015%2F07%2Ftest.jpg&f=1&nofb=1&ipt=81f5c2bb33cee7310da4b016f5b4ec00afacfc2155ba2e929d873be00fdc15bf&ipo=images"
                #         # Path(__file__).parent
                #         # / "test.png"
                #     ),
                # ),
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
            style=rx.BoxStyle(fill=theme.neutral_color),
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
        external_url=f"http://localhost:8000",
        quiet=False,
        _validator_factory=validator_factory,
    )
else:
    app = rx_app.as_fastapi(
        external_url=f"http://localhost:8000",
        _validator_factory=validator_factory,
    )
