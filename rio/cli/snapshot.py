import asyncio
import sys
from typing import *  # type: ignore


class Snapshot:
    """
    Stores the state of the current python process and allows it to be restored
    later on. Specifically:

    - Running asyncio tasks: Upon restoring any new tasks will be cancelled

    - Loaded modules: Upon restoring any new modules will be unloaded
    """

    def __init__(self):
        # Tasks currently running
        self._running_tasks = {t for t in asyncio.all_tasks() if not t.done()}

        # Modules currently loaded
        self._loaded_modules = set(sys.modules.keys())

    def restore(self) -> None:
        # Find new tasks and cancel them
        # for task in asyncio.all_tasks():
        #     if task not in self._running_tasks:
        #         task.cancel()

        # Find new modules and unload them
        for module_name in list(sys.modules.keys()):
            if module_name not in self._loaded_modules:
                del sys.modules[module_name]
