from pathlib import Path
from typing import *  # type: ignore

import rio
import rio.debug
import rio_docs

from . import article
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
                width="grow",
                height="grow",
            ),
            # Footer
            comps.Footer(),
        )


class ColumnSample(rio.Widget):
    spacing: float = 0

    def build(self) -> rio.Widget:
        return rio.Row(
            rio.Column(
                comps.SampleA(),
                comps.SampleB(),
                comps.SampleC(),
                spacing=ColumnSample.spacing,
                width="grow",
                align_x=0.5,
            ),
            rio.Card(
                rio.Column(
                    rio.Text("Spacing", style="heading3"),
                    rio.Slider(
                        min=0,
                        max=3,
                        value=ColumnSample.spacing,
                    ),
                    width=12,
                ),
                hover_height=0,
                elevate_on_hover=1,
                align_y=0,
            ),
            spacing=2,
            width="grow",
        )


def get_docs() -> rio.Widget:
    docs = rio_docs.ClassDocs.parse(rio.Column)
    rio_docs.custom.postprocess_widget_docs(docs)

    art = article.create_widget_api_docs(
        docs,
        ColumnSample,
    )

    return art.build()


routes = [
    rio.Route(
        "",
        views.HomeView,
    ),
    rio.Route(
        "documentation",
        views.DocumentationView,
        children=[
            rio.Route(
                "",
                lambda: rio.Column(
                    get_docs(),
                    rio.Spacer(),
                    margin_left=23,
                    margin_bottom=4,
                    spacing=3,
                    width=65,
                    height="grow",
                    align_x=0.5,
                ),
            ),
        ],
    ),
]


rio_app = rio.App(
    name="Rio",
    build=AppRoot,
    routes=routes,
    default_attachments=[
        theme.THEME,
    ],
    assets_dir=Path(__file__).parent / "assets",
)


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
