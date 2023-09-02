import hashlib
import secrets
from pathlib import Path
from typing import *  # type: ignore

# Random bytes added during hashing to make any internal values extremely
# difficult to guess
_HASH_SALT = secrets.token_bytes(32)


def _securely_hash_bytes_changes_between_runs(data: bytes) -> bytes:
    """
    Returns an undefined, cryptographically secure hash of the given bytes. A
    random value is added to the hash to make it difficult to guess the
    original value. This random value is the same for all hashes generated by
    this function during the same run of the program, but changes between runs.
    """

    hasher = hashlib.sha256()
    hasher.update(_HASH_SALT)
    hasher.update(data)
    return hasher.digest()


class HostedAsset:
    def __init__(
        self,
        media_type: Optional[str],
        data: Union[bytes, Path],
    ):
        # The asset's id both uniquely identifies the asset, and is used as part
        # of the asset's URL.
        #
        # It is derived from the data, so that if the same file is to be hosted
        # multiple times only one instance is actually stored. Furthermore, this
        # allows the client to cache the asset efficiently, since the URL is
        # always the same.
        if isinstance(data, bytes):
            # TODO: Consider only hashing part of the data + media type + size
            # rather than processing everything
            secret_id_prefix = "b-"
            secret_id_bytes = _securely_hash_bytes_changes_between_runs(data)
        else:
            secret_id_prefix = "f-"
            secret_id_bytes = _securely_hash_bytes_changes_between_runs(
                str(data.resolve()).encode("utf-8")
            )

        self.secret_id = secret_id_prefix + secret_id_bytes.hex()

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
