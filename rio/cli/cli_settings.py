from pathlib import Path
from typing import *  # type: ignore

import keyring
import platformdirs
import tomlkit


class SingletonClass:
    """
    Singleton class for reading and writing CLI settings.
    """

    _instance = None
    _config: Dict[str, Any]

    def __new__(cls):
        # Already initialized?
        if cls._instance is not None:
            return cls._instance

        # Nope, create a new instance
        self = cls._instance = super(SingletonClass, cls).__new__(cls)

        # Read the config
        config_dir = Path(platformdirs.user_config_dir("rio"))
        self._config = tomlkit.loads((config_dir / "config.toml").read_text())

        return self

    @property
    def auth_token(self) -> Optional[str]:
        return keyring.get_password("rio", "rioApiAuthToken")

    @auth_token.setter
    def auth_token(self, value: str) -> None:
        keyring.set_password("rio", "rioApiAuthToken", value)
