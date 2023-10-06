import inspect
from pathlib import Path
from typing import *  # type: ignore

import rio
import rio.debug
import rio_docs

from . import article
from . import components as comps
from . import pages, structure, theme

PROJECT_ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT_DIR / "assets"


def make_slideshow_placeholder(variant: int) -> rio.Component:
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


class AppRoot(rio.Component):
    def build(self) -> rio.Component:
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
            # PageView
            rio.PageView(
                width="grow",
                height="grow",
            ),
            # Footer
            comps.Footer(
                margin_top=2,
            ),
        )


class ColumnSample(rio.Component):
    spacing: float = 0

    def build(self) -> rio.Component:
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


def get_docs(component_class: Type) -> rio.Component:
    # Get the docs class for this class
    docs = rio_docs.ClassDocs.parse(component_class)

    # Generate the article. This is done differently based on whether this is a
    # component or another class.
    if issubclass(component_class, rio.Component):
        rio_docs.custom.postprocess_component_docs(docs)

        art = article.create_component_api_docs(
            docs,
            ColumnSample,
        )

    else:
        rio_docs.custom.postprocess_class_docs(docs)

        art = article.create_class_api_docs(docs)

    return art.build()


# Prepare the list of all documentation pages
def _make_documentation_pages() -> List[rio.Page]:
    result = []

    for (
        url_segment,
        section_name,
        article_name,
        article_or_class,
    ) in structure.DOCUMENTATION_STRUCTURE_LINEAR:
        if inspect.isclass(article_or_class):
            make_child = lambda rio_class=article_or_class: rio.Column(
                get_docs(rio_class),
                rio.Spacer(),
                margin_left=23,
                margin_bottom=4,
                spacing=3,
                width=65,
                height="grow",
                align_x=0.5,
            )

        else:
            make_child = lambda article=article_or_class: article().build()

        result.append(
            rio.Page(
                url_segment,
                make_child,
            )
        )

    return result


# Merge all pages
pages = [
    # Top Level Views
    rio.Page(
        "",
        pages.HomePage,
    ),
    rio.Page(
        "documentation",
        pages.DocumentationPage,
        children=[
            rio.Page(
                "",
                pages.DocumentationLandingPage,
            ),
            *_make_documentation_pages(),
        ],
    ),
]


rio_app = rio.App(
    name="Rio",
    build=AppRoot,
    pages=pages,
    default_attachments=[
        theme.THEME,
    ],
    assets_dir=Path(__file__).parent / "assets",
)


if __name__ == "__main__":
    rio_app._run_as_web_server(
        host="127.0.0.1",
        port=8001,
        quiet=False,
        validator_factory=rio.debug.Validator,
        internal_on_app_start=None,
    )
else:
    app = rio_app._as_fastapi(
        running_in_window=False,
        validator_factory=rio.debug.Validator,
        internal_on_app_start=None,
    )
