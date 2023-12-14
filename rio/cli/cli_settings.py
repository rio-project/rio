from pathlib import Path
from typing import *  # type: ignore

import keyring
import platformdirs
import revel
import tomlkit
from revel import error, fatal, print, warning

from . import api_client


class CliInstance:
    """
    Singleton class for reading and writing CLI settings.
    """

    _instance = None
    _config: tomlkit.TOMLDocument
    _api_client: Optional[api_client.RioApi]

    def __new__(cls):
        # Already initialized?
        if cls._instance is not None:
            return cls._instance

        # Nope, create a new instance
        self = cls._instance = super(CliInstance, cls).__new__(cls)

        # Read the config
        try:
            config_dir = Path(platformdirs.user_config_dir("rio"))
            self._config = tomlkit.loads((config_dir / "config.toml").read_text())
        except FileNotFoundError:
            self._config = tomlkit.document()
        except OSError as err:
            fatal(f"Couldn't read Rio's configuration: {err}")

        # Api client
        self._api_client = None

        return self

    @property
    def auth_token(self) -> Optional[str]:
        return keyring.get_password("rio", "rioApiAuthToken")

    @auth_token.setter
    def auth_token(self, value: str) -> None:
        keyring.set_password("rio", "rioApiAuthToken", value)

    async def get_api_client(self, *, logged_in: bool = True) -> api_client.RioApi:
        """
        Return an API client for the Rio API. If `logged_in` is True, the
        client will be authenticated, prompting the user to login if necessary.
        """
        # If there is no client yet, create one
        if self._api_client is None:
            self._api_client = api_client.RioApi()

        # Authenticate, if necessary
        if logged_in and not self._api_client.is_logged_in:
            raise NotImplementedError("TODO: Login")

        return self._api_client
