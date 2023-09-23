from __future__ import annotations

import abc
import hashlib
import io
import os
import secrets
from functools import lru_cache
from pathlib import Path
from typing import *  # type: ignore

import aiohttp
from PIL.Image import Image

from . import session
from .common import URL, ImageLike
from .self_serializing import SelfSerializing

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


_ASSETS: Dict[Tuple[Union[bytes, Path, URL], Optional[str]], Asset] = {}


class Asset(SelfSerializing):
    """
    Base class for assets - i.e. files that the client needs to be able to
    access. Assets can be hosted locally or remotely.

    Assets are "singletons", i.e. if you create two assets with the same input,
    they will be the same object:

        >>> Asset.new(Path("foo.png")) is Asset.new(Path("foo.png"))
        True

    To use an asset in a widget, simply store it in the widget's state. The
    asset will automatically register itself with the AppServer (if necessary)
    and serialize itself as a URL.
    """

    def __init__(
        self,
        media_type: Optional[str] = None,
    ):
        if type(self) is __class__:
            raise Exception(
                "Cannot instantiate Asset directly; use `Asset.new()` instead"
            )

        # The MIME type of the asset
        self.media_type = media_type

    @overload
    @classmethod
    def new(cls, data: bytes, media_type: Optional[str] = None) -> BytesAsset:
        ...

    @overload
    @classmethod
    def new(cls, data: Path, media_type: Optional[str] = None) -> PathAsset:
        ...

    @overload
    @classmethod
    def new(cls, data: URL, media_type: Optional[str] = None) -> UrlAsset:
        ...

    @classmethod
    def new(
        cls,
        data: Union[bytes, Path, URL],
        media_type: Optional[str] = None,
    ) -> Asset:
        key = (data, media_type)
        try:
            return _ASSETS[key]
        except KeyError:
            pass

        if isinstance(data, Path):
            asset = PathAsset(data, media_type)
        elif isinstance(data, URL):
            asset = UrlAsset(data, media_type)
        elif isinstance(data, (bytes, bytearray)):
            asset = BytesAsset(data, media_type)
        elif isinstance(data, str):
            raise TypeError(
                f"Cannot create asset from input {data!r}. Perhaps you meant to"
                f" pass a `pathlib.Path` or `rio.URL`?"
            )
        else:
            raise TypeError(f"Cannot create asset from input {data!r}")

        _ASSETS[key] = asset
        return asset

    @classmethod
    def from_image(
        cls,
        image: ImageLike,
        media_type: Optional[str] = None,
    ) -> Asset:
        if isinstance(image, Image):
            file = io.BytesIO()
            image.save(file, format="PNG")
            image = file.getvalue()
            media_type = "image/png"

        return Asset.new(image, media_type)

    @abc.abstractmethod
    async def try_fetch_as_blob(self) -> Tuple[bytes, Optional[str]]:
        """
        Try to fetch the image as blob & media type. Raises a `ValueError` if
        fetching fails.
        """
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Asset):
            return NotImplemented

        if self.media_type != other.media_type:
            return False

        if type(self) != type(other):
            return False

        return self._eq(other)

    @abc.abstractmethod
    def _eq(self, other: Asset) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def _serialize(self, sess: session.Session) -> str:
        raise NotImplementedError


class HostedAsset(Asset):
    """
    Base class for assets that are hosted locally.
    """

    def _serialize(self, sess: session.Session) -> str:
        sess._app_server.weakly_host_asset(self)
        return self.url()

    @property
    def secret_id(self) -> str:
        # The asset's id both uniquely identifies the asset, and is used as part
        # of the asset's URL.
        #
        # It is derived from the data, so that if the same file is to be hosted
        # multiple times only one instance is actually stored. Furthermore, this
        # allows the client to cache the asset efficiently, since the URL is
        # always the same.
        try:
            return self._secret_id
        except AttributeError:
            pass

        self._secret_id = self._get_secret_id()
        return self._secret_id

    def url(self, server_external_url: Optional[str] = None) -> str:
        """
        Returns the URL at which the asset can be accessed. If
        `server_external_url` is passed the result will be an absolute URL. If
        not, a relative URL is returned instead.
        """
        relative_url = f"/rio/asset/temp-{self.secret_id}"

        if server_external_url is None:
            return relative_url
        else:
            # TODO document this and/or enfoce it in the `AppServer` class already
            assert not server_external_url.endswith(
                "/"
            ), "server_external_url must not end with a slash"
            return server_external_url + relative_url

    @abc.abstractmethod
    def _get_secret_id(self) -> str:
        raise NotImplementedError


class BytesAsset(HostedAsset):
    def __init__(
        self,
        data: Union[bytes, bytearray],
        media_type: Optional[str] = None,
    ):
        super().__init__(media_type)

        self.data = data

    def _eq(self, other: BytesAsset) -> bool:
        return self.data == other.data

    async def try_fetch_as_blob(self) -> Tuple[bytes, Optional[str]]:
        return self.data, self.media_type

    def _get_secret_id(self) -> str:
        # TODO: Consider only hashing part of the data + media type + size
        # rather than processing everything
        return "b-" + _securely_hash_bytes_changes_between_runs(self.data).hex()


@lru_cache
def path_exists(path: Path) -> bool:
    return path.exists()


@lru_cache
def path_is_file(path: Path) -> bool:
    return path.is_file()


class PathAsset(HostedAsset):
    def __init__(
        self,
        path: Union[os.PathLike, str],
        media_type: Optional[str] = None,
    ):
        super().__init__(media_type)

        self.path = Path(path)
        assert path_exists(self.path), f"Asset file {self.path} does not exist"

    def _eq(self, other: PathAsset) -> bool:
        return self.path == other.path

    async def try_fetch_as_blob(self) -> Tuple[bytes, Optional[str]]:
        try:
            return self.path.read_bytes(), self.media_type
        except IOError:
            raise ValueError(f"Could not load asset from {self.path}")

    def _get_secret_id(self) -> str:
        return (
            "f-"
            + _securely_hash_bytes_changes_between_runs(
                str(self.path).encode("utf-8")
            ).hex()
        )


class UrlAsset(Asset):
    def __init__(
        self,
        url: URL,
        media_type: Optional[str] = None,
    ):
        super().__init__(media_type)

        self._url = url

    def _serialize(self, sess: session.Session) -> str:
        return str(self._url)

    def _eq(self, other: UrlAsset) -> bool:
        return self.url == other.url

    def url(self, server_external_url: Optional[str] = None) -> URL:
        return self._url

    async def try_fetch_as_blob(self) -> Tuple[bytes, Optional[str]]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self._url) as response:
                    return await response.read(), response.content_type
        except aiohttp.ClientError:
            raise ValueError(f"Could not fetch asset from {self._url}")
