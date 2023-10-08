import functools
from typing import *  # type: ignore

import rio

from .. import common


@functools.lru_cache(maxsize=None)
def _load_snippet(name: str) -> str:
    path = common.PROJECT_ROOT_DIR / "snippets" / f"{name}.py"

    if not path.exists():
        raise FileNotFoundError(f'No snippet found with name "{name}"')

    return path.read_text()


class Snippet(rio.Component):
    """
    Loads a Python snippet from `<project-root>/snippets/<snippet-name>.py` and
    renders it as a code block.
    """

    name: str

    def build(self) -> rio.Component:
        # Fetch the snippet source code
        source = _load_snippet(self.name)

        # Wrap it in a markdown code block
        return rio.MarkdownView(
            f"```python\n{rio.escape_markdown_code(source)}\n```",
            default_language="python",
        )
