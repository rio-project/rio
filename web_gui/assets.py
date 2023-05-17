import secrets
from pathlib import Path
from typing import Union


class HostedAsset:
    def __init__(
        self,
        name: str,
        mime_type: str,
        data: Union[bytes, Path],
    ):
        # The asset's id both uniquely identifies the asset, and is used as part
        # of the asset's URL. Thus it acts as secret, preventing users from
        # accessing assets without permission.
        self.secret_id = secrets.token_urlsafe()

        # Human-readable name of the asset. This is used for debugging purposes
        self.name = name

        # The MIME type of the asset
        self.media_type = mime_type

        # The asset's data. This can either be a bytes object, or a path to a
        # file containing the asset's data. The file must exist for the duration
        # of the asset's lifetime.
        self.data = data

        if isinstance(data, Path):
            assert data.exists(), f"Asset file {data} does not exist"
