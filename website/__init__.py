from pathlib import Path
from typing import *  # type: ignore

import rio
import rio.debug

from . import components as comps
from . import theme, views

PROJECT_ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT_DIR / "assets"


def make_slideshow_placeholder(variant: int) -> rio.Widget:
    colors = [
        rio.Color.RED,
        rio.Color.GREEN,
        rio.Color.BLUE,
        rio.Color.YELLOW,
        rio.Color.PURPLE,
        rio.Color.MAGENTA,
    ]

    return rio.Rectangle(
        child=rio.Text(
            f"Slideshow Page {variant}",
        ),
        style=rio.BoxStyle(
            fill=colors[variant % len(colors)],
        ),
        width="grow",
        height="grow",
    )


class AppRoot(rio.Widget):
    def build(self) -> rio.Widget:
        return rio.Column(
            # Navbar (sticky)
            rio.Sticky(
                comps.NavigationBar(
                    height=4,
                    width="grow",
                    align_y=0,
                ),
            ),
            # Router
            rio.Router(
                rio.Route(
                    "",
                    views.HomeView,
                ),
                rio.Route(
                    "documentation",
                    views.DocumentationView,
                ),
                width="grow",
                height="grow",
            ),
            # Footer
            comps.Footer(),
        )


rio_app = rio.App(
    name="Rio",
    route=rio.Route(
        "",
        AppRoot,
        children=[
            rio.Route(
                "",
                views.HomeView,
            ),
            rio.Route(
                "documentation",
                views.DocumentationView,
            ),
        ],
    ),
    routes={
        "/": rio.Route(
            AppRoot,
        ),
        "/documentation": rio.Route(
            "documentation",
            views.DocumentationView,
        ),
    },
    default_attachments=[
        theme.THEME,
    ],
    assets_dir=Path(__file__).parent / "assets",
)


@rio_app.route("/slideshow")
def slideshow() -> rio.Widget:
    pass


if __name__ == "__main__":
    rio_app.run_as_web_server(
        port=8001,
        external_url_override="http://localhost:8001",
        quiet=False,
        _validator_factory=rio.debug.Validator,
    )
else:
    app = rio_app._as_fastapi(
        external_url_override="http://localhost:8001",
        _validator_factory=rio.debug.Validator,
    )
