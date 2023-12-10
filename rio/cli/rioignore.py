import enum
from pathlib import Path
from typing import *  # type: ignore

import gitignore_parser

__all__ = [
    "FileMatch",
    "RioIgnore",
]


class FileMatch(enum.Enum):
    INCLUDED = enum.auto()
    PARTIALLY_INCLUDED = enum.auto()
    EXCLUDED = enum.auto()


class RioIgnore:
    """
    Parses `.rioignore` files and allows querying whether a given path should be
    ignored.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir.resolve()
        self._patterns = []

    def add_pattern(self, line: str) -> None:
        line = line.rstrip("\n")
        pattern = gitignore_parser.rule_from_pattern(
            line,
            base_path=self.base_dir,
            source=(None, len(self._patterns)),
        )

        if not pattern:
            return

        self._patterns.append(pattern)

    def add_patterns_from_file(self, file_path: TextIO) -> None:
        for line in file_path.readlines():
            self.add_pattern(line)

    def get_file_match(self, path: Path) -> FileMatch:
        raise NotImplementedError()
