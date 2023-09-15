from pathlib import Path
from typing import *  # type: ignore

import reflex as rx
import reflex.debug

from . import components as comps
from . import theme, views

PROJECT_ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT_DIR / "assets"


def make_slideshow_placeholder(variant: int) -> rx.Widget:
    colors = [
        rx.Color.RED,
        rx.Color.GREEN,
        rx.Color.BLUE,
        rx.Color.YELLOW,
        rx.Color.PURPLE,
        rx.Color.MAGENTA,
    ]

    return rx.Rectangle(
        child=rx.Text(
            f"Slideshow Page {variant}",
        ),
        style=rx.BoxStyle(
            fill=colors[variant % len(colors)],
        ),
        width="grow",
        height="grow",
    )


class AppRoot(rx.Widget):
    active_route: str = ""

    def build(self) -> rx.Widget:
        return rx.Column(
            # Navbar (sticky)
            rx.Sticky(
                comps.NavigationBar(
                    # active_route=AppRoot.active_route,
                    active_route=self.active_route,
                    height=4,
                    width="grow",
                    align_y=0,
                ),
            ),
            # Router
            rx.Router(
                rx.Route(
                    "",
                    views.HomeView,
                ),
                rx.Route(
                    "documentation",
                    views.DocumentationView,
                ),
                width="grow",
                height="grow",
            ),
            # Footer
            comps.Footer(),
        )


rx_app = rx.App(
    name="Reflex",
    build=AppRoot,
    default_attachments=[
        theme.THEME,
    ],
    assets_dir=Path(__file__).parent / "assets",
)


if __name__ == "__main__":
    rx_app.run_as_web_server(
        port=8001,
        external_url_override="http://localhost:8001",
        quiet=False,
        _validator_factory=reflex.debug.Validator,
    )
else:
    app = rx_app.as_fastapi(
        external_url_override="http://localhost:8001",
        _validator_factory=reflex.debug.Validator,
    )
