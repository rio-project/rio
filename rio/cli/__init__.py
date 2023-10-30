from pathlib import Path
from typing import *  # type: ignore

import revel
import uvicorn
from revel import error, fatal, print, success, warning
from typing_extensions import TypeAlias

import rio.snippets

from . import project_setup, rio_toml

__all__ = [
    "app",
]

app = revel.App()


@app.command
def new(
    nicename: str,
    *,
    type: Literal["app", "website"],
    template: Optional[project_setup.TemplatesLiteral] = None,
) -> None:
    # Project setup is surprisingly complex. Don't handle it here
    project_setup.create_project(
        nicename=nicename,
        type=type,
        template=template,
    )


@app.command
def run(
    *,
    port: int = 8080,
    public: bool = False,
) -> None:
    # Load the config file
    project_dir = Path.cwd()
    config = rio_toml.try_load(project_dir)

    # TODO: Verify the parameters are okay. i.e. `port` is a valid port number

    # Delegate to uvicorn
    uvicorn.run(
        f"{config.main_module}:{config.fastapi_app_variable}",
        host="0.0.0.0" if public else "127.0.0.1",
        port=port,
        reload=True,
    )
