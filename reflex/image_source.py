import io
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, Union

import aiohttp
from PIL.Image import Image

from . import assets


class ImageSource:
    def __init__(
        self,
        image: "ImageLike",
        *,
        media_type: Optional[str] = None,
    ):
        if isinstance(image, ImageSource):
            self._url = image._url
            self._asset = image._asset

        elif isinstance(image, str):
            self._url = image
            self._asset = None

        elif isinstance(image, Path):
            if media_type is None:
                media_type, _ = mimetypes.guess_type(image)

                if media_type is None:
                    raise ValueError(f"Could not guess MIME type for `{image}`")

            self._url = None
            self._asset = assets.HostedAsset(
                media_type,
                data=image,
            )

        else:
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")

            self._url = None
            self._asset = assets.HostedAsset(
                "image/png",
                data=buffer.getvalue(),
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageSource):
            return NotImplemented

        return self._url == other._url and self._asset == other._asset

    def __hash__(self) -> int:
        return hash((self._url, self._asset))

    async def _try_fetch_as_blob(self) -> Tuple[bytes, str]:
        """
        Try to fetch the image as blob & media type. Raises a `ValueError` if
        fetching fails.
        """
        # URL
        if self._url is not None:
            async with aiohttp.ClientSession() as session:
                async with session.get(self._url) as response:
                    if response.status != 200:
                        raise ValueError(f"Failed to fetch favicon from {self._url}.")

                    return await response.read(), response.content_type

        # Straight bytes
        assert self._asset is not None
        if isinstance(self._asset.data, bytes):
            return self._asset.data, self._asset.media_type

        # File
        assert isinstance(self._asset.data, Path)
        try:
            return self._asset.data.read_bytes(), self._asset.media_type
        except (FileNotFoundError, IOError, OSError):
            raise ValueError(f"Failed to read image from {self._asset.data}")


ImageLike = Union[Path, Image, str, ImageSource]
