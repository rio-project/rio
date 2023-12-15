import tomllib
from pathlib import Path
from typing import *  # type: ignore


class TomlConfig:
    def __init__(
        self,
        config_path: Path,
        *,
        default: Dict[str, Any] = {},
    ):
        self.config_path = config_path
        self.default = default
        self._config = None

    def _load(self) -> Dict[str, Any]:
        """
        Load the current contents of the file and convert them to a dictionary.
        If the file cannot be read, return the default.
        """
