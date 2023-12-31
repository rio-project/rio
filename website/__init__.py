import inspect
from pathlib import Path
from typing import *  # type: ignore

import rio
import rio.debug
import rio_docs

from . import article_models
from . import components as comps
from . import pages, structure, theme

PROJECT_ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT_DIR / "assets"


class AppRoot(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            # Navigation Bar
            rio.Overlay(
                comps.NavigationBar(height=4, width="grow", margin_top=1.0, align_y=0),
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


def get_docs(component_class: Type) -> rio.Component:
    # Get the docs class for this class
    docs = rio_docs.ClassDocs.parse(component_class)

    # Get the interactive examples for this class
    try:
        example = getattr(comps, f"{component_class.__name__}Example")
    except AttributeError:
        example = None

    # Generate the article. This is done differently based on whether this is a
    # component or another class.
    if issubclass(component_class, rio.Component):
        rio_docs.custom.postprocess_component_docs(docs)

        art = article_models.create_component_api_docs(
            docs,
            example,
        )

    else:
        rio_docs.custom.postprocess_class_docs(docs)

        art = article_models.create_class_api_docs(docs)

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
            make_child = lambda rio_class=article_or_class: get_docs(rio_class)
        else:
            make_child = lambda article=article_or_class: article().build()

        result.append(
            rio.Page(
                url_segment,
                lambda make_child=make_child: rio.Column(
                    make_child(),
                    rio.Spacer(),
                    margin_left=30,
                    margin_right=2,
                    margin_bottom=4,
                    spacing=3,
                    width=65,
                    height="grow",
                    align_x=0.5,
                ),
            )
        )

    return result


# Merge all pages
all_pages = [
    # Top Level Views
    rio.Page(
        "",
        pages.HomePage,
        # Just for debugging
        # TODO / REMOVEME
        # guard=lambda x: rio.URL("/documentation"),
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


app = rio.App(
    name="Rio",
    build=AppRoot,
    # build=lambda: rio.Text("foooooO!"),
    icon=rio.common.RIO_LOGO_ASSET_PATH,
    pages=all_pages,
    theme=theme.THEME,
    assets_dir=ASSETS_DIR,
)
