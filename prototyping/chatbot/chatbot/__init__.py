from pathlib import Path
from typing import *  # type: ignore

import rio
import rio.debug

from . import pages

PROJECT_ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT_DIR / "assets"


app = rio.App(
    name="Rio",
    pages=[
        rio.Page("", pages.ChatPage),
    ],
    # theme=rio.Theme.pair_from_color(
    #     color_headings=True,
    # ),
)
