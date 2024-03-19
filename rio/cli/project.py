import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

import gitignore_parser
import revel
import tomlkit
import tomlkit.exceptions
import tomlkit.items
import uniserde
from revel import *  # type: ignore
from revel import fatal

from . import rioignore

__all__ = [
    "RioProject",
]

T = TypeVar("T")


DEFAULT_FATAL = object()
DEFAULT_KEYERROR = object()


class RioProject:
    def __init__(
        self,
        file_path: Path,
        toml_dict: uniserde.JsonDoc,
        ignores: rioignore.RioIgnore,
    ):
        # Path to the `rio.toml` file. May or may not exist
        self._file_path = file_path

        # All of the data from the `rio.toml` file
        self._toml_dict = toml_dict

        # Which sections & keys have been modified and thus must be written back
        # to the `rio.toml` file
        self._dirty_keys: Set[Tuple[str, str]] = set()

        # Contains the parsed `.rioignore` file. When called with a path, it
        # returns True if the path should be ignored as per the `.rioignore`
        # file.
        self.ignores = ignores

        # Any rules which should be added to the `.rioignore` file. These are
        # just strings which are appended to the end of the file, one per line.
        self.rioignore_additions: List[str] = []

    def get_key(
        self,
        section_name: str,
        key_name: str,
        type: Type[T],
        default_value: Any,
    ) -> T:
        """
        Fetches the value of a key from the `rio.toml` file. If the key is
        missing, and a default value was provided it is returned instead.

        If the default value is `DEFAULT_FATAL`, an error is displayed and the
        program exits.

        If the default value is `DEFAULT_KEYERROR`, a `KeyError` is raised.
        """
        # Try to get the section
        section: Dict[str, Any]

        try:
            section = self._toml_dict[section_name]  # type: ignore
        except KeyError:
            if default_value is DEFAULT_FATAL:
                fatal(
                    f"`rio.toml` is missing the `{section_name}` section",
                    status_code=1,
                )

            if default_value is DEFAULT_KEYERROR:
                raise KeyError(key_name)

            section: Dict[str, Any] = {}

        # Try to get the key
        try:
            value = section[key_name]

        # There is no value, use the default
        except KeyError:
            if default_value is DEFAULT_FATAL:
                fatal(
                    f"`rio.toml` is missing the `{key_name}` key. Please add it to the [[{section_name}] section.",
                    status_code=1,
                )

            if default_value is DEFAULT_KEYERROR:
                raise KeyError(key_name)

            value = default_value

        # Make sure the value is the correct type
        if not isinstance(value, type):
            fatal(
                f"`rio.toml` contains an invalid value for `{key_name}`: expected {type}, got {type(value)}",
                status_code=1,
            )

        # Done
        return value

    def set_key(self, section_name: str, key_name: str, value: Any) -> None:
        """
        Sets the value of a key in the `rio.toml` file. The value is not written
        to disk until `write()` is called.
        """
        # Get the section
        try:
            section = self._toml_dict[section_name]
        except KeyError:
            section = self._toml_dict[section_name] = {}

        # Make sure the section is indeed a section
        if not isinstance(section, dict):
            fatal(
                f"`rio.toml` contains an invalid value for `{section_name}`: this should be a section, not `{type(section)}`",
                status_code=1,
            )

        # Set the key
        section[key_name] = value
        self._dirty_keys.add((section_name, key_name))

    @property
    def project_directory(self) -> Path:
        return self._file_path.parent

    @property
    def module_path(self) -> Path:
        folder = self.project_directory

        # If a `src` directory exists, look there
        src_dir = folder / "src"
        if src_dir.exists():
            folder = src_dir

        # If a package (folder) exists, use that
        module_path = folder / self.app_main_module
        if module_path.exists():
            return module_path

        # Otherwise there must be a file
        return module_path.with_name(self.app_main_module + ".py")

    @property
    def app_type(self) -> Literal["app", "website"]:
        result = self.get_key("app", "app_type", str, "website")

        if result not in ("app", "website"):
            fatal(
                f"`rio.toml` contains an invalid value for `app.app_type`: It should be either `app` or `website`, not `{result}`"
            )

        return result

    @property
    def app_main_module(self) -> str:
        return self.get_key("app", "main_module", str, DEFAULT_FATAL)

    @property
    def app_variable(self) -> str:
        return self.get_key("app", "app_variable", str, "app")

    @property
    def deploy_name(self) -> str:
        # Is a name already stored in the `rio.toml`?
        try:
            return self.get_key("deploy", "name", str, DEFAULT_KEYERROR)
        except KeyError:
            pass

        # Ask the user for a name, and make sure it's suitable for URLs
        print(
            "What should your app be called? This name will be used as part of the URL."
        )
        print(
            'For example, if you name your app "my-app", it will be deployed at `https://rio.dev/.../my-app`.'
        )

        while True:
            name = input("App name: ")

            allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789-"
            normalized = re.sub("[^" + allowed_chars + "]", "-", name.lower())

            if name == normalized:
                break

            normalized = re.sub("-+", "-", normalized)
            print(f"`{name}` cannot be used for app names. Is `{normalized}` okay?")

            if revel.select_yes_no("", default_value=True):
                name = normalized
                break

        # Store the name
        self.set_key("deploy", "name", name)
        return name

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
            rio_toml_dict = tomlkit.load(rio_toml_path.open()).unwrap()

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
        except tomlkit.exceptions.TOMLKitError as e:
            fatal(
                f"There is a problem with `rio.toml`: {e}",
                status_code=1,
            )

        # If a `.rioignore` file exists, parse it
        rioignore_path = project_dir / ".rioignore"
        ignores = rioignore.RioIgnore(base_dir=project_dir)

        try:
            with rioignore_path.open() as f:
                ignores.add_patterns_from_file(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            fatal(
                f"Couldn't read `.rioignore`: {e}",
                status_code=1,
            )

        # Instantiate the project
        return RioProject(
            file_path=rio_toml_path,
            toml_dict=rio_toml_dict,
            ignores=ignores,
        )

    def __enter__(self) -> "RioProject":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        # Make sure to write any changes back to the `rio.toml` file
        self.write()

    def _write_rio_toml(self) -> None:
        # Are there even any changes to write?
        if not self._dirty_keys:
            return

        logging.debug(f"Writing `{self._file_path}`")

        # Make sure the parent directory exists
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        # Fetch an up-to-date copy of the file contents, with all formatting
        # intact
        try:
            new_toml_dict = tomlkit.loads(self._file_path.read_text())

        # If it can't be read, preserve all known values
        except (OSError, tomlkit.exceptions.TOMLKitError) as e:
            new_toml_dict = tomlkit.TOMLDocument()

            self._dirty_keys.clear()
            for section_name, section in self._toml_dict.items():
                if not isinstance(section, dict):
                    continue

                for key_name, value in section.items():
                    self._dirty_keys.add((section_name, key_name))

        # Update the freshly read toml with all latent changes
        for section_name, key_name in self._dirty_keys:
            try:
                section = new_toml_dict[section_name]
            except KeyError:
                section = new_toml_dict[section_name] = tomlkit.table()

            section[key_name] = self._toml_dict[section_name][key_name]  # type: ignore

        # Write the file
        try:
            with self._file_path.open("w") as f:
                tomlkit.dump(new_toml_dict, f)

        except OSError as e:
            fatal(
                f"Couldn't write `{self._file_path}`: {e}",
                status_code=1,
            )

        # The project's keys are now clean
        self._dirty_keys.clear()

    def _write_rioignore(self) -> None:
        # Are there even any changes to write?
        if not self.rioignore_additions:
            return

        # Make sure the parent directory exists
        rioignore_path = self.project_directory / ".rioignore"
        rioignore_path.parent.mkdir(parents=True, exist_ok=True)

        # Append the lines to the file
        try:
            with rioignore_path.open("a") as f:
                f.write("\n\n")

                for line in self.rioignore_additions:
                    f.write(line)
                    f.write("\n")

        except OSError as e:
            fatal(
                f"Couldn't write `.rioignore`: {e}",
                status_code=1,
            )

    def write(self) -> None:
        """
        Write any changes back to the `rio.toml` file.
        """
        # Write the `rio.toml` file
        self._write_rio_toml()

        # Write any additions to the `.rioignore` file
        self._write_rioignore()
