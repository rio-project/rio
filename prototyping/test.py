import asyncio
import json
from pathlib import Path
from typing import Any, Callable, Optional

import PIL.Image

import web_gui as wg

CORPOPRATE_YELLOW = wg.Color.from_rgb(0.98, 0.91, 0.0)


class LoginWidget(wg.Widget):
    username: str = ""
    password: str = ""

    sap_session_token: str = ""

    async def login(self) -> None:
        print("CLICKEDY!")
        self.sap_session_token = "..."

    def build(self) -> wg.Widget:
        return wg.Column(
            children=[
                wg.TextInput(text=LoginWidget.username),
                wg.TextInput(text=LoginWidget.password),
                wg.Button(
                    "Login",
                    on_press=self.login,
                ),
            ],
        )


class MainPage(wg.Widget):
    sap_session_token: str = ""

    def build(self) -> wg.Widget:
        return wg.Rectangle(
            fill=CORPOPRATE_YELLOW,
            child=wg.Align(
                wg.Override(
                    wg.Margin(
                        LoginWidget(
                            sap_session_token=MainPage.sap_session_token,
                        ),
                        margin_left=4,
                    ),
                    width=30,
                    height=15,
                ),
                align_y=0.35,
            ),
        )


def main():
    app = wg.App(
        "Super Dynamic Website!",
        MainPage,
        icon=PIL.Image.open("./prototyping/icon.png"),
    )
    app.run(quiet=False)


if __name__ == "__main__":
    # asyncio.run(main())
    main()
