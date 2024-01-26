from pathlib import Path
from typing import *  # type: ignore

import rio
import rio.debug

from . import components as comps
from . import pages, structure, theme

PROJECT_ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT_DIR / "assets"


rio.Icon.register_single_icon(
    ASSETS_DIR / "accent-shape-logo.svg",
    "self",
    "accent-shape-logo",
)


rio.Icon.register_single_icon(
    ASSETS_DIR / "accent-shape-corner-bottom-right.svg",
    "self",
    "accent-shape-corner-bottom-right",
)

rio.Icon.register_single_icon(
    ASSETS_DIR / "brands" / "discord-logo.svg",
    "thirdparty",
    "discord-logo",
)

rio.Icon.register_single_icon(
    ASSETS_DIR / "brands" / "github-logo.svg",
    "thirdparty",
    "github-logo",
)


# TODO: Temporary, until included in the rio package
rio.Icon.register_single_icon(
    rio.common.PROJECT_ROOT_DIR / "raw-icons/styling/corner-round-bottom-right.svg",
    "styling",
    "rounded-corner-bottom-right",
)

rio.Icon.register_single_icon(
    rio.common.PROJECT_ROOT_DIR / "raw-icons/styling/corner-round-bottom-left.svg",
    "styling",
    "rounded-corner-bottom-left",
)


class AppRoot(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Overlay(
                comps.NavigationBar(
                    height=3.5, width="grow", margin_top=1.0, align_y=0
                ),
            ),
            rio.PageView(
                width="grow",
                height="grow",
            ),
            comps.Footer(
                # margin_top=2,
            ),
        )


def _make_documentation_pages() -> list[rio.Page]:
    """
    Generates all documentation pages, as well as their children.
    """
    result = []

    for section in structure.DOCUMENTATION_STRUCTURE:
        # None is used to indicate whitespace
        if section is None:
            continue

        # Construct the section page
        section_name, section_url, builders = section
        section_page = rio.Page(
            name=section_name,
            page_url=section_url,
            build=rio.PageView,
        )
        result.append(section_page)

        # Add all the pages in this section
        for builder in builders:
            sub_page = rio.Page(
                builder.url_segment,
                lambda builder=builder: builder.build().build(),
            )
            section_page.children.append(sub_page)

    return result


# Merge all pages
all_pages = [
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


app = rio.App(
    name="Rio",
    build=AppRoot,
    icon=rio.common.RIO_LOGO_ASSET_PATH,
    pages=all_pages,
    theme=theme.THEME,
    assets_dir=ASSETS_DIR,
)
