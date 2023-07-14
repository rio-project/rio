import secrets
from pathlib import Path
from typing import *  # type: ignore


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

    def url(self, server_external_url: Optional[str] = None) -> str:
        """
        Returns the URL at which the asset can be accessed. If
        `server_external_url` is passed the result will be an absolute URL. If
        not, a relative URL is returned instead.
        """

        relative_url = f"/reflex/asset/temp-{self.secret_id}"

        if server_external_url is None:
            return relative_url
        else:
            # TODO document this and/or enfoce it in the `AppServer` class already
            assert not server_external_url.endswith(
                "/"
            ), "server_external_url must not end with a slash"
            return server_external_url + relative_url

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HostedAsset):
            return NotImplemented

        if self.media_type != other.media_type:
            return False

        if isinstance(self.data, bytes) and isinstance(other.data, bytes):
            return self.data is other.data

        return self.data == other.data
