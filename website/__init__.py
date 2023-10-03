import inspect
from pathlib import Path
from typing import *  # type: ignore

import rio
import rio.debug
import rio_docs

from . import article
from . import components as comps
from . import structure, theme, views

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
            # Navigation Bar
            rio.Sticky(
                comps.NavigationBar(
                    height=4,
                    width="grow",
                    margin_top=1.0,
                    align_y=0,
                ),
            ),
            # Spacer for the navigation bar
            rio.Spacer(height=5.1),
            # Router
            rio.Router(
                width="grow",
                height="grow",
            ),
            # Footer
            comps.Footer(
                margin_top=2,
            ),
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
                align_y=0,
                elevate_on_hover=True,
            ),
            spacing=2,
            width="grow",
        )


def get_docs(widget_class: Type[rio.Widget]) -> rio.Widget:
    docs = rio_docs.ClassDocs.parse(widget_class)
    rio_docs.custom.postprocess_widget_docs(docs)

    art = article.create_widget_api_docs(
        docs,
        ColumnSample,
    )

    return art.build()


# Prepare the list of all documentation routes
def _make_documentation_routes() -> List[rio.Route]:
    result = []

    for (
        url_segment,
        section_name,
        article_name,
        article_or_widget,
    ) in structure.DOCUMENTATION_STRUCTURE_LINEAR:
        if inspect.isclass(article_or_widget) and issubclass(
            article_or_widget, rio.Widget
        ):
            make_child = lambda widget_class=article_or_widget: rio.Column(
                get_docs(widget_class),
                rio.Spacer(),
                margin_left=23,
                margin_bottom=4,
                spacing=3,
                width=65,
                height="grow",
                align_x=0.5,
            )

        else:
            make_child = lambda article=article_or_widget: article().build()

        result.append(
            rio.Route(
                url_segment,
                make_child,
            )
        )

    return result


# Merge all routes
routes = [
    # Top Level Views
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
                views.DocumentationLandingPage,
            ),
            *_make_documentation_routes(),
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
