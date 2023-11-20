import logging
from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

import revel
import toml
import uniserde
from revel import *  # type: ignore
from revel import fatal

__all__ = [
    "RioProject",
]

T = TypeVar("T")


class RioProject:
    def __init__(self, file_path: Path, toml_dict: uniserde.JsonDoc):
        # Path to the `rio.toml` file. May or may not exist
        self._file_path = file_path

        # All of the data from the `rio.toml` file
        self._toml_dict = toml_dict

        # Which keys have been modified and thus must be written back to the
        # `rio.toml` file
        self._dirty_keys: Set[str] = set()

    def _get_key(
        self,
        key_name: str,
        type: Type[T],
        default_value: Any,
    ) -> T:
        # Try to fetch the value from the toml file
        try:
            value = self._toml_dict[key_name]

        # There is no value, use the default
        except KeyError:
            self._toml_dict[key_name] = default_value
            self._dirty_keys.add(key_name)
            return default_value

        # Make sure the value is the correct type
        if not isinstance(value, type):
            fatal(
                f"`rio.toml` contains an invalid value for `{key_name}`: expected {type}, got {type(value)}",
                status_code=1,
            )

        # Done
        return value

    @property
    def main_module(self) -> str:
        return self._get_key("main_module", str, "TODO")

    @property
    def fastapi_app_variable(self) -> str:
        return self._get_key("fastapi_app_variable", str, "fastapi_app")

    @property
    def debug_port(self) -> int:
        return self._get_key("debug_port", int, 0)

    @staticmethod
    def try_load() -> "RioProject":
        """
        Best-effort attempt to locate the project directory and load the
        `rio.toml` file.
        """
        # Search upward until a `rio.toml` is found
        root_search_dir = Path.cwd()
        project_dir = root_search_dir

        while True:
            # Is this the project directory?
            rio_toml_path = project_dir / "rio.toml"

            if rio_toml_path.exists():
                break

            # Go up a directory, if possible
            parent_dir = project_dir.parent

            if parent_dir == project_dir:
                project_dir = root_search_dir
                break

            project_dir = parent_dir

        # Try to load the toml file
        rio_toml_path = project_dir / "rio.toml"
        logging.debug(f"Loading `{rio_toml_path}`")

        try:
            rio_toml_dict = toml.load(rio_toml_path)

        # No such file. Offer to create one
        except FileNotFoundError:
            warning(
                f"You don't appear to be inside of a Rio project. Would you like to create one?"
            )

            if not revel.select_yes_no("", default_value=True):
                fatal(
                    f"Couldn't find any a `rio.toml` file.",
                    status_code=1,
                )

            rio_toml_dict = {}

        # Anything OS related
        except OSError as e:
            fatal(
                f"Cannot read `{rio_toml_path}`: {e}",
                status_code=1,
            )

        # Invalid syntax
        except toml.TomlDecodeError as e:
            fatal(
                f"There is a syntax error in the `rio.toml` file: {e}",
                status_code=1,
            )

        # Done, return the project
        return RioProject(
            file_path=rio_toml_path,
            toml_dict=rio_toml_dict,  # type: ignore
        )

    def __enter__(self) -> "RioProject":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        # Make sure to write any changes back to the `rio.toml` file
        if self._dirty_keys:
            self.write()

    def write(self) -> None:
        """
        Write any changes back to the `rio.toml` file.
        """
        logging.debug(f"Writing `{self._file_path}`")

        # Make sure the parent directory exists
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        try:
            with self._file_path.open("w") as f:
                toml.dump(self._toml_dict, f)

        except OSError as e:
            fatal(
                f"Couldn't write `{self._file_path}`: {e}",
                status_code=1,
            )
