import time
from pathlib import Path
from typing import *  # type: ignore

import watchfiles

from .. import project
from . import run_models


class FileWatcherWorker:
    def __init__(
        self,
        *,
        push_event: Callable[[run_models.Event], None],
        proj: project.RioProject,
    ) -> None:
        self.push_event = push_event
        self.proj = proj

    async def run(self) -> None:
        """
        Watch the project directory for changes and report them as events.
        """
        # Only care for certain files
        filter = watchfiles.PythonFilter()

        # Watch the project directory
        async for changes in watchfiles.awatch(
            self.proj.project_directory, watch_filter=filter
        ):
            for change, path in changes:
                path = Path(path)

                # Not all files trigger a reload
                if not self._file_triggers_reload(path):
                    continue

                # Report the change
                self.push_event(
                    run_models.FileChanged(
                        time.monotonic_ns(),
                        path,
                    )
                )

    def _file_triggers_reload(self, path: Path) -> bool:
        """
        Returns True if the given file should trigger a reload of the project.
        """

        if path.suffix == ".py":
            return True

        # TODO: While a change to `rio.toml` should absolutely trigger a reload,
        #   the other code doesn't currently actually reload the project. Hence
        #   it would be confusing to display a reload to the user without
        #   actually doing anything.
        #
        # if path.name in ("rio.toml",):
        #     return True

        return False
