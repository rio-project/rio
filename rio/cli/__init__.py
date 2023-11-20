from pathlib import Path
from typing import *  # type: ignore

import revel
import uvicorn
from revel import error, fatal, print, success, warning
from typing_extensions import TypeAlias

import rio.snippets

from . import project, project_setup

__all__ = [
    "app",
]

revel.GLOBAL_STYLES.add_alias("primary", ["magenta"])
revel.GLOBAL_STYLES.add_alias("bg-primary", ["bg-magenta"])

app = revel.App(
    summary="An easy to use, app & web framework for Python",
    details="""
Rio is a framework for building reactive apps and websites in Python. It's
designed to be easy to use, and to get out of your way as much as possible.

This is the command line interface for Rio. You can use it to easily create new
projects, run them, and more.
""",
)


@app.command(
    aliases={"init", "create"},
    summary="Create a new Rio project",
    details="""
The `new` command creates a new directory and populates it with the files needed
to start a new Rio project. You can optionally specify a template, in which case
the files from that template will be copied into the new project, allowing you
hit the ground running.
""",
    parameters=[
        revel.Parameter(
            "nicename",
            summary="Human-readable name for the new project",
            prompt="What should the project be called?",
        ),
        revel.Parameter(
            "type",
            summary="Whether to create a website or an app",
        ),
        revel.Parameter(
            "template",
            summary="Template to use for the new project",
        ),
    ],
)
def new(
    nicename: str,
    *,
    type: Literal["app", "website"],
    template: Optional[project_setup.TemplatesLiteral] = None,
) -> None:
    # Project setup is surprisingly complex. Handle it in another file
    project_setup.create_project(
        nicename=nicename,
        type=type,
        template=template,
    )


@app.command(
    summary="Run the current project",
    parameters=[
        revel.Parameter(
            "port",
            summary="Port to run the HTTP server on",
        ),
        revel.Parameter(
            "public",
            summary="Whether the app should be available on the local network, or just the local device",
        ),
    ],
)
def run(
    *,
    port: Optional[int] = None,
    public: bool = False,
) -> None:
    # TODO: Verify the parameters are okay. i.e. `port` is a valid port number

    # Load the project
    with project.RioProject.try_load() as proj:
        main_module = proj.main_module
        fastapi_app_variable = proj.fastapi_app_variable

    # Delegate to uvicorn
    uvicorn.run(
        f"{main_module}:{fastapi_app_variable}",
        host="0.0.0.0" if public else "127.0.0.1",
        port=proj.debug_port if port is None else port,
        reload=True,
    )
