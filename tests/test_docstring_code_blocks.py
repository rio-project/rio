import re
import subprocess
import tempfile
from typing import *  # type: ignore

import black
import pyright
import revel
import rio_docs
from revel import print, print_chapter

import rio

CODE_BLOCK_PATTERN = re.compile(r"```.*?\n(.*?)\n```", re.DOTALL)


def all_components() -> Iterable[Type[rio.Component]]:
    """
    Iterates over all components that ship with Rio.
    """
    to_do: Iterable[Type[rio.Component]] = [rio.Component]

    while to_do:
        component = to_do.pop()
        yield component
        to_do.extend(component.__subclasses__())


def verify_code_block(source: str) -> None:
    assert source.startswith("```")
    assert source.endswith("```")

    # Split into language and source
    linebreak = source.index("\n")
    assert linebreak != -1
    first_line = source[3:linebreak].strip()
    source = source[linebreak + 1 : -3]

    # Make sure a language is specified
    assert first_line, "No language specified"

    # Make sure the source is valid Python
    try:
        result = compile(source, "<string>", "exec")
    except SyntaxError as e:
        raise SyntaxError(f"Syntax error in {first_line} code block: {e}")

    # Make sure the string is properly formatted
    formatted_source = black.format_str(source, mode=black.FileMode())

    if formatted_source != source:
        raise ValueError(f"Code block is not properly formatted:\n{formatted_source}")

    # Run static analysis on the code
    with tempfile.NamedTemporaryFile(suffix=".py") as f:
        f.write("import rio\n".encode("utf-8"))
        f.write(formatted_source.encode("utf-8"))
        f.flush()

        proc = pyright.run(
            f.name,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result_out = proc.stdout
        assert isinstance(result_out, bytes), type(result_out)
        result_out = result_out.decode()

        match = re.search(
            r"(\d+) error(s)?, (\d+) warning(s)?, (\d+) information",
            result_out,
        )
        assert match is not None, result_out

        n_errors = int(match.group(1))
        if n_errors:
            raise ValueError(f"Code block has {n_errors} errors:\n{result_out}")


def main() -> None:
    # Find all component classes
    components = list(all_components())

    # Get their docstrings
    for comp in components:
        print_chapter(comp.__name__)
        docs = rio_docs.ClassDocs.parse(comp)

        # No docs?
        if docs.details is None:
            print("No docs")
            continue

        # Find any contained code blocks
        for match in CODE_BLOCK_PATTERN.finditer(docs.details):
            verify_code_block(match.group(0))


if __name__ == "__main__":
    main()
