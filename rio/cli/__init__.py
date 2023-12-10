import sys
from typing import *  # type: ignore

import revel
from revel import error, fatal, print, success, warning

from . import project, project_setup, run_project

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
            summary="Whether the app should be available on the local network, rather than just the local device",
        ),
        revel.Parameter(
            "quiet",
            summary="Suppresses HTTP logs and other noise",
        ),
    ],
    details="""
The `run` command runs the current project for debugging. If your project is a
website, it will be hosted on a local HTTP server, and you can view it in your
browser. If the project is a app, it will be displayed in a window instead.

Rio will constantly watch your project for changes, and automatically reload
the app or website when it detects a change. This makes it easy to iterate on
your project without having to manually restart it.

The `port` and `public` options are ignored if the project is an app, since
they only make sense for websites.
""",
)
def run(
    *,
    port: Optional[int] = None,
    public: bool = False,
    quiet: bool = True,
) -> None:
    with project.RioProject.try_load() as proj:
        # Some options only make sense for websites
        if proj.app_type == "app":
            if port is not None:
                port = None
                warning(
                    "Ignoring the `port` option, since this project is not a website"
                )

            if public:
                public = False
                warning(
                    "Ignoring the `public` option, since this project is not a website"
                )

        runner = run_project.RunningApp(
            proj=proj,
            port=port,
            public=public,
            quiet=quiet,
            debug_mode=True,
            run_in_window=proj.app_type == "app",
        )
        runner.run()
