import secrets
from pathlib import Path
from typing import Union


class HostedAsset:
    def __init__(
        self,
        media_type: str,
        data: Union[bytes, Path],
    ):
        # The asset's id both uniquely identifies the asset, and is used as part
        # of the asset's URL. Thus it acts as secret, preventing users from
        # accessing assets without permission.
        self.secret_id = secrets.token_urlsafe()

        # The MIME type of the asset
        self.media_type = media_type

        # The asset's data. This can either be a bytes object, or a path to a
        # file containing the asset's data. The file must exist for the duration
        # of the asset's lifetime.
        self.data = data

        if isinstance(data, Path):
            assert data.exists(), f"Asset file {data} does not exist"

    def url(self, server_external_url: str) -> str:
        # TODO document this and/or enfoce it in the `AppServer` class already
        assert not server_external_url.endswith(
            "/"
        ), "server_external_url must not end with a slash"

        return f"{server_external_url}/asset/{self.secret_id}"
