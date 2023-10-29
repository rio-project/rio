import functools
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

import uniserde

from .. import common

SECTION_PATTERN = re.compile(r"#\s*<(\/?[\w-]+)>")

_ALL_SNIPPET_PATHS: Optional[Dict[str, Path]] = None


@dataclass
class Snippet(uniserde.Serde):
    raw_code: str

    def get_section(self, section_name: str) -> str:
        # Find the target section
        lines = self.raw_code.splitlines()
        section_found = False
        result = []

        for line in lines:
            match = SECTION_PATTERN.match(line)

            # No match
            if match is None:
                result.append(line)
                continue

            # Start of the target section?
            if match.group(1) == section_name:
                result = []
                section_found = True
                continue

            # End of the target section?
            if match.group(1) == f"/{section_name}":
                return "\n".join(result)

            # Some other section, drop it
            pass

        # The section was never found
        if not section_found:
            raise KeyError(f'There is no section named "{section_name}"')

        # The section was found, but never closed
        raise ValueError(f'The section "{section_name}" was never closed')

    def stripped_code(self) -> str:
        """
        Returns the given code with all section tags removed.
        """
        lines = self.raw_code.splitlines()

        # Remove all section tags
        result = []
        for line in lines:
            if SECTION_PATTERN.match(line) is None:
                result.append(line)

        return "\n".join(result)


def _scan_snippets() -> None:
    """
    Find all snippets in the snippet directory, and initialize the
    `_ALL_SNIPPET_PATHS` global variable.
    """
    global _ALL_SNIPPET_PATHS
    assert _ALL_SNIPPET_PATHS is None

    # Find all snippet files
    _ALL_SNIPPET_PATHS = {}

    def scan_dir_recursively(group_name: str, path: Path) -> None:
        assert path.is_dir(), path
        assert _ALL_SNIPPET_PATHS is not None

        for fpath in path.iterdir():
            # Directory
            if fpath.is_dir():
                scan_dir_recursively(group_name, fpath)

            # Snippet file
            else:
                key = f"{group_name}/{fpath.name}"
                _ALL_SNIPPET_PATHS[key] = fpath

    # Scan all snippet directories. The first directory is used as a key, the
    # rest just for organization.
    for group_dir in common.SNIPPETS_DIR.iterdir():
        assert group_dir.is_dir(), group_dir
        scan_dir_recursively(group_dir.name, group_dir)


@functools.lru_cache(maxsize=None)
def get_raw_snippet(name: str) -> Snippet:
    """
    Returns the contents of the snippet file with the given name. Raises a
    `KeyError` if no such snippet exists.

    The snippet isn't processed in any way, meaning all tags and metadata are
    still present.
    """
    # Make sure the snippets have been scanned
    if _ALL_SNIPPET_PATHS is None:
        _scan_snippets()

    assert _ALL_SNIPPET_PATHS is not None

    # Try to read the metadata. Fall back to an empty dict if it doesn't exist.

    try:
        json_path = _ALL_SNIPPET_PATHS[f"{name}.json"]
    except KeyError:
        metadata = {}
    else:
        with json_path.open() as json_file:
            metadata = json.load(json_file)

    # Read the snippet code
    snippet_path = _ALL_SNIPPET_PATHS[f"{name}.py"]
    try:
        metadata["rawCode"] = snippet_path.read_text()
    except KeyError:
        raise KeyError(f'There is no snippet named "{name}"') from None

    # Deserialize the snippet
    return Snippet.from_json(metadata)


@functools.lru_cache(maxsize=None)
def get_snippet_section(
    snippet_name: str,
    *,
    section: Optional[str] = None,
) -> str:
    """
    Returns the contents of the specified section in the given snippet. Raises a
    `KeyError` if no such snippet exists.
    """
    snippet = get_raw_snippet(snippet_name)

    # If no section name was given, return the entire snippet
    if section is None:
        return snippet.stripped_code()

    # Otherwise, return the specified section
    return snippet.get_section(section)
