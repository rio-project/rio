import logging
from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

import gitignore_parser
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
    def __init__(
        self,
        file_path: Path,
        toml_dict: uniserde.JsonDoc,
        ignore_func: Callable[[str], bool],
    ):
        # Path to the `rio.toml` file. May or may not exist
        self._file_path = file_path

        # All of the data from the `rio.toml` file
        self._toml_dict = toml_dict

        # Which keys have been modified and thus must be written back to the
        # `rio.toml` file
        self._dirty_keys: Set[str] = set()

        # Contains the parsed `.rioignore` file. When called with a path, it
        # returns True if the path should be ignored as per the `.rioignore`
        # file.
        self._ignore_func: Callable[[str], bool] = ignore_func

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

    def _set_key(self, key_name: str, value: Any) -> None:
        self._toml_dict[key_name] = value
        self._dirty_keys.add(key_name)

    @property
    def project_directory(self) -> Path:
        return self._file_path.parent

    @property
    def main_module(self) -> str:
        return self._get_key("main_module", str, "TODO")

    @property
    def app_variable(self) -> str:
        return self._get_key("app_variable", str, "app")

    @property
    def debug_port(self) -> int:
        return self._get_key("debug_port", int, 0)

    @property
    def app_type(self) -> Literal["app", "website"]:
        result = self._get_key("app_type", str, "website")

        if result not in ("app", "website"):
            warning(
                f"`rio.toml` contains an invalid value for `app_type`: expected `app` or `website`, got `{result}`"
            )
            result = "website"
            self._set_key("app_type", result)

        return result

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

        # If a `.rioignore` file exists, parse it
        rioignore_path = project_dir / ".rioignore"

        if rioignore_path.exists() and rioignore_path.is_file():
            try:
                ignore_func = gitignore_parser.parse_gitignore(rioignore_path)

            except OSError as e:
                fatal(
                    f"Couldn't read `.rioignore`: {e}",
                    status_code=1,
                )
        else:
            ignore_func = lambda _: False

        # Instantiate the project
        return RioProject(
            file_path=rio_toml_path,
            toml_dict=rio_toml_dict,
            ignore_func=ignore_func,
        )

    def is_ignored(self, path: Path) -> bool:
        """
        Given a path, determine whether it should be ignored, as per the
        `.rioignore` file.
        """
        return self._ignore_func(str(path))

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
