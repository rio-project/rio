from typing import Literal

import introspection
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
    template: project_setup.TemplatesLiteral | None = None,
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
            "release",
            summary="Switches between release and debug mode",
        ),
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
    release: bool = False,
    port: int | None = None,
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

        # Running a project comes with considerable complexity. All of that is
        # crammed into classes.
        arbiter = run_project.Arbiter(
            proj=proj,
            port=port,
            public=public,
            quiet=quiet,
            debug_mode=not release,
            run_in_window=proj.app_type == "app",
        )
        arbiter.run()


@app.command(
    summary="Add a page or component to the project",
    parameters=[
        revel.Parameter(
            "what",
            summary="Whether to add a `page` or a `component`",
        ),
        revel.Parameter(
            "name",
            summary="The name of the new page or component",
        ),
    ],
    details="""
The `add` command adds a new page or component to your project. A python file
containing some template code will be created in the `pages` or `components`
folder of your project.
""",
)
def add(what: Literal["page", "component"], /, name: str) -> None:
    if what == "page":
        raise NotImplementedError("FIXME: Adding pages is not yet supported")

    with project.RioProject.try_load() as proj:
        module_path = proj.module_path
        if not module_path.is_dir():
            error(
                f"Cannot add {what}s to a single-file project. Please convert"
                f" your project into a package."
            )
            return

        # Make sure the `pages` or `components` folder exists
        folder_path = module_path / (what + "s")
        folder_path.mkdir(exist_ok=True)

        # Create the new file
        name = name.strip().replace(" ", "_")
        file_name = introspection.convert_case(name, "snake")
        class_name = introspection.convert_case(name, "pascal")

        file_path = folder_path / (file_name + ".py")
        if file_path.exists():
            error(f"File {file_path.relative_to(module_path)} already exists")
            return

        file_path.write_text(
            f"""
from __future__ import annotations

from typing import *  # type: ignore

import rio

from .. import components as comps


__all__ = ['{class_name}']


class {class_name}(rio.Component):
    example_state: str = "For demonstration purposes"

    def build(self) -> rio.Component:
        return rio.Text(self.example_state)
"""
        )

        # Import the module in the __init__.py
        init_py_path = file_path.with_name("__init__.py")
        try:
            init_py_code = init_py_path.read_text(encoding="utf8")
        except FileNotFoundError:
            init_py_code = ""
        init_py_code = init_py_code.rstrip() + f"\nfrom .{file_name} import *\n"
        init_py_path.write_text(init_py_code, encoding="utf8")

        success(
            f"New {what} created at {file_path.relative_to(proj.project_directory)}"
        )
