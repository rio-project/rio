import asyncio
import json
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, Type

import PIL.Image

import web_gui as wg
from web_gui.widgets.fundamentals import Widget

CORPOPRATE_YELLOW = wg.Color.from_rgb(0.98, 0.91, 0.0)
CORPORATE_GREY = wg.Color.from_rgb(0.69, 0.69, 0.69)
CORPORATE_BLUE = wg.Color.from_rgb(0.0, 0.47, 0.78)


class CorporateCard(wg.Widget):
    child: wg.Widget
    heading: Optional[str] = None

    def build(self) -> wg.Widget:
        radius = 0.0
        margin = 0.5

        if self.heading is None:
            heading_child = wg.Override(
                wg.Rectangle(
                    fill=wg.Color.BLACK,
                    corner_radius=(radius, radius, 0, 0),
                ),
                height=0.5,
            )
        else:
            heading_child = wg.Rectangle(
                fill=wg.Color.BLACK,
                child=wg.Margin(
                    wg.Text(
                        self.heading,
                        font_color=wg.Color.WHITE,
                        font_weight="bold",
                        font_size=1.2,
                    ),
                    margin=margin,
                ),
                corner_radius=(radius, radius, 0, 0),
            )

        return wg.Column(
            [
                heading_child,
                wg.Rectangle(
                    fill=CORPOPRATE_YELLOW,
                    child=wg.Margin(
                        self.child,
                        margin=margin,
                    ),
                    corner_radius=(0, 0, radius, radius),
                ),
            ]
        )


class LoginWidget(wg.Widget):
    username: str = ""
    password: str = ""

    sap_session_token: Optional[str] = None

    on_login: wg.EventHandler[[]] = None

    async def login(self) -> None:
        self.sap_session_token = "<totally-legit-session-token>"
        await wg.call_event_handler(self.on_login)

    def build(self) -> wg.Widget:
        return CorporateCard(
            wg.Column(
                children=[
                    wg.Margin(
                        wg.TextInput(
                            text=LoginWidget.username,
                            placeholder="Benuztername",
                        ),
                        margin_bottom=1,
                    ),
                    wg.Margin(
                        wg.TextInput(
                            text=LoginWidget.password,
                            placeholder="Passwort",
                        ),
                        margin_bottom=1,
                    ),
                    wg.Button(
                        "Login",
                        on_press=self.login,
                    ),
                ],
            ),
            heading="Login",
        )


class SimpleMenu(wg.Widget):
    heading: str
    children: List[str]

    def build(self) -> Widget:
        child_widgets = []

        for ii, name in enumerate(self.children):
            child_widgets.append(
                wg.Margin(
                    wg.Button(
                        name,
                        on_press=lambda: print(f"Pressed {name}"),
                    ),
                    margin_top=0 if ii == 0 else 0.5,
                )
            )

        return wg.Override(
            CorporateCard(
                heading=self.heading,
                child=wg.Column(child_widgets),
            ),
            width=30,
        )


class MainPage(wg.Widget):
    sap_session_token: Optional[str] = None

    def on_login(self) -> None:
        print(f"Logged in! The session token is {self.sap_session_token}.")

    def build_login_view(self) -> wg.Widget:
        return wg.Align(
            wg.Override(
                wg.Margin(
                    LoginWidget(
                        sap_session_token=MainPage.sap_session_token,
                        on_login=self.on_login,
                    ),
                    margin_left=4,
                ),
                width=30,
                height=15,
            ),
            align_y=0.35,
        )

    def build_menu(self):
        return wg.Align(
            wg.Column(
                [
                    SimpleMenu(
                        "Reports",
                        [
                            "Personalbericht",
                            "Zustellbericht",
                        ],
                    ),
                    wg.Margin(
                        SimpleMenu(
                            "Tasks",
                            [
                                "Scheduler",
                                "Laufende Tasks",
                            ],
                        ),
                        margin_top=1,
                    ),
                ]
            ),
            align_x=0.5,
            align_y=0.3,
        )

    def build(self) -> wg.Widget:
        if self.sap_session_token is None:
            child = self.build_login_view()
        else:
            child = self.build_menu()

        return wg.Rectangle(
            fill=wg.Color.GREY,
            child=child,
        )


wg_app = wg.App(
    "Super Dynamic Website!",
    MainPage,
    icon=PIL.Image.open("./dev_testing/icon.png"),
    port=3000,
)
app = wg_app.api


if __name__ == "__main__":
    wg_app.run_as_website(quiet=False)
