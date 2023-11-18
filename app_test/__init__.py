from dataclasses import field
from pathlib import Path
from typing import *  # type: ignore

import rio
import rio.debug

theme = rio.Theme.from_color()


rio_app = rio.App(
    name="Rio Showcase",
    build=rio.AppRoot,
    default_attachments=[
        theme,
    ],
)


fastapi_app = rio_app.as_fastapi()
