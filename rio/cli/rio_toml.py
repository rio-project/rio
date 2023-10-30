from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

import toml
import uniserde
from revel import fatal

__all__ = [
    "RioToml",
    "try_load",
]


@dataclass
class RioToml:
    # The name of the python module which contains the Rio app. This will be
    # passed to uvicorn to run, along with the name of the variable which
    # contains the FastAPI app.
    main_module: str

    # The name of the variable in the main module which contains the FastAPI
    # app. This will be passed to uvicorn to run, along with the name of the
    # main module.
    fastapi_app_variable: str

    # TODO:
    # - How are dependencies managed? Literal['poetry', 'conda', 'requirements.txt', 'other']


def try_load(project_directory: Path) -> "RioToml":
    # Try to load the toml file
    try:
        rio_toml_path = project_directory / "rio.toml"
        rio_toml_dict = toml.load(rio_toml_path)

    # Not found
    except FileNotFoundError:
        fatal(
            "Could not find `rio.toml` in the project directory."
        )  # TODO: Explain how to make one, or which command to run

    # Parse it
    return uniserde.from_json(
        rio_toml_dict,
        RioToml,
    )
