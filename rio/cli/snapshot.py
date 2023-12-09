import asyncio
import ctypes
import sys
import threading
from typing import *  # type: ignore


class RestoreException(BaseException):
    """
    Raised in threads that were not running when the snapshot was taken in
    order to kill them.
    """

    pass


# def ctype_async_raise(target_tid: int, exception: Type[BaseException]) -> None:
#     """
#     Raises an exception in a thread identified by target_tid.

#     Source: https://gist.github.com/liuw/2407154
#     """
#     ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(
#         ctypes.c_long(target_tid),
#         ctypes.py_object(exception),
#     )

#     # ref: http://docs.python.org/c-api/init.html#PyThreadState_SetAsyncExc

#     if ret == 0:
#         raise ValueError(f"There is no active thread with id {target_tid}")

#     elif ret > 1:
#         # This shouldn't happen, but since killing threads is hardly a supported
#         # feature things can go wrong - handle them. Well, try to.
#         ctypes.pythonapi.PyThreadState_SetAsyncExc(target_tid, 0)
#         raise SystemError("PyThreadState_SetAsyncExc failed")


class Snapshot:
    """
    Stores the state of the current python process and allows it to be restored
    later on. Specifically:

    - Running threads: Upon restoring any new threads will have an exception
      raised in an attempt to kill them

    - Running asyncio tasks: Upon restoring any new tasks will be cancelled

    - Loaded modules: Upon restoring any new modules will be unloaded
    """

    def __init__(self):
        # # Ids of currently running threads
        # self._thread_identifiers = {t.ident: t for t in threading.enumerate()}

        # Tasks currently running
        self._running_tasks = {t for t in asyncio.all_tasks() if not t.done()}

        # Modules currently loaded
        self._loaded_modules = set(sys.modules.keys())

    def restore(self) -> None:
        # # Find new threads and raise an exception in them
        # for task in threading.enumerate():
        #     if task.ident not in self._thread_identifiers:
        #         if task.ident is not None:
        #             ctype_async_raise(task.ident, RestoreException)

        # Find new tasks and cancel them
        for task in asyncio.all_tasks():
            if task not in self._running_tasks:
                task.cancel()

        # Find new modules and unload them
        for module_name in list(sys.modules.keys()):
            if module_name not in self._loaded_modules:
                del sys.modules[module_name]
