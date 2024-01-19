from pathlib import Path
from typing import *  # type: ignore

import revel
from revel import error, fatal, input, print, success, warning
from typing_extensions import TypeAlias

import rio.cli
import rio.snippets

__all__ = [
    "create_project",
    "TemplatesLiteral",
]

# A literal type that represents the available templates
TemplatesLiteral: TypeAlias = Literal["biography"]

# The available templates, as runtime accessible set
AVAILABLE_TEMPLATES: set[str] = set(get_args(TemplatesLiteral))

# Which snippets must be included for each project template
#
# The first page will be used as the main page, i.e. it will be located at `/`.
# The URLs of other pages are derived from the snippet name.
TEMPLATE_DEPENDENCIES: dict[TemplatesLiteral | None, set[str]] = {
    None: {
        # Components
        "common-templates/sample_component.py",
        # Pages
        "common-templates/sample_page.py",
    },
    "biography": {
        # Assets
        # "tutorial-biography/jane-doe.jpg",
        # "tutorial-biography/john-doe.jpg",
        # Components
        "tutorial-biography/about_me.py",
        "tutorial-biography/contact.py",
        "tutorial-biography/history.py",
        "tutorial-biography/projects.py",
        "tutorial-biography/skill_bars.py",
        # Pages
        "tutorial-biography/biography_page.py",
    },
}


def class_name_from_snippet_name(file_name: str) -> str:
    """
    Given a file name, determine the name of the class that is defined in it.

    e.g. `sample_component.py` -> `SampleComponent`
    """
    assert file_name.endswith(".py")
    assert file_name.count("/") == 1, file_name
    file_name = file_name.split("/")[1][:-3]
    parts = file_name.split("_")
    return "".join(part.capitalize() for part in parts)


def write_init_file(fil: IO, snippets: Iterable[rio.snippets.Snippet]) -> None:
    """
    Write an `__init__.py` file that imports all of the snippets.

    e.g. if told to import snippets `foo.py` and `bar.py`, it will write:

    ```
    from .foo import Foo
    from .bar import Bar
    ```
    """
    for snippet in snippets:
        assert snippet.name.count("/") == 1, snippet.name
        module_name = snippet.name.split("/")[1][:-3]
        class_name = class_name_from_snippet_name(snippet.name)
        fil.write(f"from .{module_name} import {class_name}\n")


def find_all_dependency_snippets(
    base_snippets: Iterable[str],
) -> list[rio.snippets.Snippet]:
    """
    Given a set of snippet names, determine the full set of all snippets that
    must be included to satisfy all dependencies. This includes the base
    snippets as well.
    """
    dependencies: list[rio.snippets.Snippet] = []
    visited_names: set[str] = set(base_snippets)
    to_do: list[str] = list(visited_names)

    while to_do:
        # Fetch the snippet
        snippet_name = to_do.pop()
        snippet = rio.snippets.get_raw_snippet(snippet_name)

        # Add the snippet to the dependencies
        dependencies.append(snippet)

        # Recursively process all of its dependencies
        for child_name in snippet.dependencies:
            if child_name in visited_names:
                continue

            visited_names.add(child_name)
            to_do.append(child_name)

    assert len(visited_names) == len(dependencies), (visited_names, dependencies)
    return dependencies


def generate_root_init(
    fil: TextIO,
    nicename: str,
    project_type: Literal["app", "website"],
    dependencies: Iterable[rio.snippets.Snippet],
    main_page_snippet_name: str,
) -> None:
    # The root component depends on the type of project
    root_component_name = (
        "rio.PageView"  # TODO: Add other components, once they're supported
    )

    # Prepare the different pages
    page_strings = []
    for dep in dependencies:
        if dep.target_directory != "pages":
            continue

        # What's the URL segment for this page?
        if dep.name == main_page_snippet_name:
            url_segment = ""
        else:
            assert dep.name.count("/") == 1, dep.name
            url_segment = dep.name.split("/")[1][:-3]
            url_segment = url_segment.replace("_", "_").lower()

        page_strings.append(
            f"""
        rio.Page(
            page_url={url_segment!r},
            build=pages.{class_name_from_snippet_name(dep.name)},
        ),"""
        )

    page_string = "\n".join(page_strings)

    # Write the result
    fil.write(
        f"""
from typing import *  # type: ignore

import rio

from . import pages
from . import components as comps


# Define a theme for Rio to use.
#
# You can modify the colors here to adapt the appearance of your app or website.
# The most important parameters are listed, but more are available! You can find
# them all in the docs TODO: Add link.
theme = rio.Theme.from_color(
    primary_color=rio.Color.from_hex("b002ef"),
    secondary_color=rio.Color.from_hex("329afc"),
    light=True,
)


# Create the Rio app
app = rio.App(
    name={nicename!r},
    build={root_component_name},
    pages=[{page_string}
    ],
    theme=theme,
)

""".lstrip()
    )

    if project_type == "website":
        fil.write(
            """
# Make the website available as a FastAPI app
#
# This allows you to run it either via the `rio run` command, or using tools
# such as `uvicorn`.
fastapi_app = app.as_fastapi()
"""
        )


def create_project(
    *,
    nicename: str,
    type: Literal["app", "website"],
    template: TemplatesLiteral | None = None,
) -> None:
    """
    Create a new project with the given name. This will directly interact with
    the terminal, asking for input and printing output.
    """

    # Derive the python name from the nicename
    python_name = nicename.strip().replace("-", "_").replace(" ", "_").lower()

    # If the python name is not a valid module name, ask for a different one
    if not python_name.isidentifier():
        print(
            f"`{nicename}` is not a valid Python module name. What should the module be called?"
        )

        def parse_module_name(name: str) -> str:
            if not name.isidentifier():
                raise ValueError()

            return name

        python_name = input("Module name", parse=parse_module_name)

    # Create the target directory
    project_dir = Path.cwd() / nicename
    project_dir.mkdir(parents=True, exist_ok=True)

    # If the project directory already exists it must be empty
    if any(project_dir.iterdir()):
        fatal(f"The project directory `{project_dir}` already exists and is not empty")

    # Create the config file
    with open(project_dir / "rio.toml", "w") as f:
        f.write("# This is the configuration file for Rio,\n")
        f.write("# an easy to use app & web framework for Python.\n")
        f.write("\n")
        f.write(f"[app]\n")
        f.write(f'app_type = "{type}"  # This is either "website" or "app"\n')
        f.write(f'main_module = "{python_name}"  # The name of your Python module\n')

    # Create the main module and its subdirectories
    main_module_dir = project_dir / python_name
    main_module_dir.mkdir()
    (main_module_dir / "components").mkdir()
    (main_module_dir / "pages").mkdir()
    (main_module_dir / "assets").mkdir()

    # Determine all components and pages that should be copied over
    dependencies: list[rio.snippets.Snippet] = find_all_dependency_snippets(
        TEMPLATE_DEPENDENCIES[template]
    )

    # Copy over all of the dependencies
    for snippet in dependencies:
        assert snippet.target_directory in ("components", "pages"), (
            snippet.name,
            snippet.target_directory,
        )

        assert snippet.name.count("/") == 1, snippet.name
        target_filename = snippet.name.split("/")[1]
        target_path = main_module_dir / snippet.target_directory / target_filename

        target_path.write_text(snippet.stripped_code())

    # Find the main page
    for main_page_snippet in dependencies:
        if main_page_snippet.target_directory == "pages":
            break
    else:
        raise AssertionError(f"Template `{template}` has no main page!?")

    # Generate /project/__init__.py
    with open(main_module_dir / "__init__.py", "w") as fil:
        generate_root_init(
            fil=fil,
            nicename=nicename,
            project_type=type,
            dependencies=dependencies,
            main_page_snippet_name=main_page_snippet.name,
        )

    # Generate /project/pages/__init__.py
    with open(main_module_dir / "pages" / "__init__.py", "w") as f:
        write_init_file(
            f,
            [snip for snip in dependencies if snip.target_directory == "pages"],
        )

    # Generate /project/components/__init__.py
    with open(main_module_dir / "components" / "__init__.py", "w") as f:
        write_init_file(
            f,
            [snip for snip in dependencies if snip.target_directory == "components"],
        )

    # Generate README.md
    #
    # This file isn't strictly necessary, but `poetry install` in particular
    # fails without. So hey, why not make a template.
    with open(project_dir / "README.md", "w") as f:
        f.write(
            f"""# {nicename}

This is a placeholder README for your project. Use it to describe what your
project is about, to give new users a quick overview of what they can expect.

_{nicename.capitalize()} was created using [Rio](http://rio.dev/), an easy to use
app & website framework for Python._
"""
        )

    # Applications require a `__main__.py` as well
    if type == "app":
        with open(main_module_dir / "__main__.py", "w") as f:
            f.write(
                f"""
# Make sure the project is in the Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Import the main module
import {python_name}

# Run the app
{python_name}.app.run_in_window()
"""
            )

    # Report success
    #
    # TODO: Add a command to install dependencies? Activate the venv?
    print()
    success(f"The project has been created!")
    success(f"You can find it at `{project_dir.resolve()}`")
    print()
    print(f"To see your new project in action, run the following commands:")
    print(f"> cd {revel.shell_escape(project_dir.resolve())}")
    print(f"> rio run")
