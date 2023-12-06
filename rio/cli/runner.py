"""
This is a standalone script that hosts Rio project in a webserver. It is used by
the Rio CLI to run projects in separate processes.
"""

import asyncio
import importlib
import os
import sys
from pathlib import Path

import uvicorn

import rio


async def main() -> None:
    # Parse the command line arguments
    assert len(sys.argv) == 6, sys.argv
    _, project_dir, module_path, rio_app_variable, host, port = sys.argv

    project_dir = Path(project_dir)
    port = int(port)

    # Switch to the project directory
    os.chdir(project_dir)

    # Load the project module
    module = importlib.import_module(module_path)

    # Get the Rio app
    try:
        rio_app = getattr(module, rio_app_variable)
    except AttributeError:
        raise AttributeError(
            f"Module {module_path!r} has no attribute {rio_app_variable!r}"
        )

    # Make sure the variable really contains a Rio app
    if not isinstance(rio_app, rio.App):
        raise TypeError(
            f"Variable {rio_app_variable!r} in module {module_path!r} is not a Rio app"
        )

    # Run the app
    rio_app.run_as_web_server(
        host=host,
        port=port,
        quiet=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
