from pathlib import Path
from typing import Any, List, Optional

import PIL.Image

import reflex as rx
import reflex.validator

PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent
GENERATED_DIR = PROJECT_ROOT_DIR / "generated"


CORPORATE_YELLOW = rx.Color.from_rgb(0.98, 0.91, 0.0)
CORPORATE_GREY = rx.Color.from_rgb(0.69, 0.69, 0.69)
CORPORATE_BLUE = rx.Color.from_rgb(0.0, 0.47, 0.78)


class CorporateCard(rx.Widget):
    child: rx.Widget
    heading: Optional[str] = None

    def build(self) -> rx.Widget:
        radius = 0.0
        margin = 0.5

        if self.heading is None:
            heading_child = rx.Rectangle(
                fill=rx.Color.BLACK,
                corner_radius=(radius, radius, 0, 0),
                height=0.5,
            )
        else:
            heading_child = rx.Rectangle(
                fill=rx.Color.BLACK,
                child=rx.Text(
                    self.heading,
                    font_color=rx.Color.WHITE,
                    font_weight="bold",
                    font_size=1.2,
                    margin=margin,
                ),
                corner_radius=(radius, radius, 0, 0),
            )

        return rx.Column(
            [
                heading_child,
                rx.Rectangle(
                    fill=CORPORATE_YELLOW,
                    child=self.child,
                    corner_radius=(0, 0, radius, radius),
                ),
            ],
            key="you",
        )


class LoginWidget(rx.Widget):
    username: str = ""
    password: str = ""

    sap_session_token: Optional[str] = None

    on_login: rx.EventHandler[[]] = None

    async def login(self, _: rx.ButtonPressedEvent) -> None:
        self.sap_session_token = "<totally-legit-session-token>"
        await rx.call_event_handler(self.on_login)

    def build(self) -> rx.Widget:
        return CorporateCard(
            rx.Column(
                children=[
                    rx.TextInput(
                        text=LoginWidget.username,
                        placeholder="Benutzername",
                        margin_bottom=1,
                    ),
                    rx.TextInput(
                        text=LoginWidget.password,
                        placeholder="Passwort",
                        secret=True,
                        margin_bottom=1,
                    ),
                    rx.Button(
                        "Login",
                        on_press=self.login,
                        major=True,
                    ),
                    rx.Switch(),
                    rx.Dropdown({"foo": 1, "bar": 2}, on_change=print),
                ],
            ),
            heading="Login",
        )


class SimpleMenu(rx.Widget):
    heading: str
    children: List[str]

    def build(self) -> rx.Widget:
        child_widgets = []

        for ii, name in enumerate(self.children):
            child_widgets.append(
                rx.Button(
                    name,
                    on_press=lambda _: print(f"Pressed {name}"),
                    major=True,
                    margin_top=0 if ii == 0 else 0.5,
                )
            )

        return CorporateCard(
            heading=self.heading,
            child=rx.Column(child_widgets),
            width=30,
        )


class MainPage(rx.Widget):
    sap_session_token: Optional[str] = None

    def on_login(self) -> None:
        print(f"Logged in! The session token is {self.sap_session_token}.")

    def build_login_view(self) -> rx.Widget:
        return LoginWidget(
            sap_session_token=MainPage.sap_session_token,
            on_login=self.on_login,
            margin_left=4,
            width=30,
            height=15,
            align_y=0.35,
        )

    def build_menu(self):
        return rx.Column(
            [
                SimpleMenu(
                    "Reports",
                    [
                        "Personalbericht",
                        "Zustellbericht",
                    ],
                ),
                SimpleMenu(
                    "Tasks",
                    [
                        "Scheduler",
                        "Laufende Tasks",
                    ],
                    margin_top=1,
                ),
            ],
            align_x=0.5,
            align_y=0.3,
        )

    def build(self) -> rx.Widget:
        print(f"Rebuilding. The session token is {self.sap_session_token}.")

        if self.sap_session_token is None:
            child = self.build_login_view()
        else:
            child = self.build_menu()

        return rx.Rectangle(
            # fill=rx.Color.GREY,
            fill=rx.ImageFill(
                Path("./dev_testing/test.png"),
                fill_mode="stretch",
            ),
            child=child,
        )


def validator_factory() -> reflex.validator.Validator:
    return reflex.validator.Validator(
        dump_directory_path=GENERATED_DIR,
    )


rx_app = rx.App(
    "Super Dynamic Website!",
    MainPage,
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
