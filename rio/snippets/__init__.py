import functools
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

import uniserde

from .. import common

SECTION_PATTERN = re.compile(r"#\s*<(\/?\w+)>")


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


@functools.lru_cache(maxsize=None)
def get_raw_snippet(name: str) -> Snippet:
    """
    Returns the contents of the snippet file with the given name. Raises a
    `KeyError` if no such snippet exists.

    The snippet isn't processed in any way, meaning all tags and metadata are
    still present.
    """

    # Try to read the metadata. Fall back to an empty dict if it doesn't exist.
    with (common.SNIPPETS_DIR / f"{name}.json").open() as json_path:
        try:
            metadata = json.load(json_path)
        except FileNotFoundError:
            metadata = {}

    # Read the snippet code
    snippet_path = common.SNIPPETS_DIR / f"{name}.py"
    try:
        metadata["rawCode"] = snippet_path.read_text()
    except FileNotFoundError:
        raise KeyError(f'There is no snippet named "{name}"') from None

    # Deserialize the snippet
    return Snippet.from_json(metadata)


@functools.lru_cache(maxsize=None)
def get_snippet_section(
    snippet_name: str,
    *,
    section_name: Optional[str] = None,
) -> str:
    """
    Returns the contents of the specified section in the given snippet. Raises a
    `KeyError` if no such snippet exists.
    """
    snippet = get_raw_snippet(snippet_name)

    # If no section name was given, return the entire snippet
    if section_name is None:
        return snippet.stripped_code()

    # Otherwise, return the specified section
    return snippet.get_section(section_name)
