from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import *  # type: ignore

import rio

from . import component_base


__all__ = [
    "DevelComponent",
]

_SOURCE_DIRECTORY: Optional[Path] = None

_CSS_SOURCE: str = ""
_JS_SOURCE: str = ""


class DevelComponent(component_base.FundamentalComponent):
    @classmethod
    def initialize(cls, directory_path: Path):
        global _SOURCE_DIRECTORY, _CSS_SOURCE, _JS_SOURCE

        # Make sure the component is only initialized once
        if _SOURCE_DIRECTORY is not None:
            raise RuntimeError("DevelComponent is already initialized")

        # Keep track of the source directory
        _SOURCE_DIRECTORY = directory_path

        assert (
            _SOURCE_DIRECTORY.exists()
        ), "`DevelComponent` source directory does not exist"
        assert (
            _SOURCE_DIRECTORY.is_dir()
        ), "`DevelComponent` source directory is not a directory"

        # Find the input files
        scss_path = _SOURCE_DIRECTORY / "styles.scss"
        ts_path = _SOURCE_DIRECTORY / "script.ts"

        if not scss_path.exists():
            raise RuntimeError(
                "Missing `styles.scss` in `DevelComponent` source directory"
            )

        if not ts_path.exists():
            raise RuntimeError(
                "Missing `script.ts` in `DevelComponent` source directory"
            )

        # Compile the scss source
        css_path = Path(tempfile.NamedTemporaryFile(suffix=".css", delete=False).name)
        subprocess.run(["sass", str(scss_path), str(css_path)], check=True)
        assert css_path.exists(), "Sass compilation failed"
        print(f"DevelComponent: The compiled CSS is at {css_path}")

        # Compile the typescript source
        js_path = Path(tempfile.NamedTemporaryFile(suffix=".js", delete=False).name)
        subprocess.run(["tsc", str(ts_path), "--outFile", str(js_path)], check=True)
        assert js_path.exists(), "Typescript compilation failed"
        print(f"DevelComponent: The compiled JS is at {js_path}")

        # Read the source files
        _CSS_SOURCE = css_path.read_text()
        _JS_SOURCE = js_path.read_text()

    @classmethod
    def build_javascript_source(cls, sess: rio.Session) -> str:
        print("build js called")
        if _SOURCE_DIRECTORY is None:
            raise RuntimeError("`DevelComponent` is not initialized")

        return _JS_SOURCE

    @classmethod
    def build_css_source(cls, sess: rio.Session) -> str:
        print("build css called")
        if _SOURCE_DIRECTORY is None:
            raise RuntimeError("`DevelComponent` is not initialized")

        return _CSS_SOURCE
