from dataclasses import field
from pathlib import Path
from typing import *  # type: ignore

import rio
import rio.debug

theme = rio.Theme.from_color()


app = rio.App(
    name="App Showcase",
    build=rio.AppRoot,
    default_attachments=[
        theme,
    ],
)


fastapi_app = app.as_fastapi()
