import hashlib
import os
import re
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

from PIL.Image import Image
from typing_extensions import Annotated
from yarl import URL

__all__ = ["ImageLike", "Readonly", "FileInfo", "EventHandler"]


_SECURE_HASH_SEED: bytes = secrets.token_bytes(32)

# Expose common paths on the filesystem
PACKAGE_ROOT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT_DIR = PACKAGE_ROOT_DIR.parent

GENERATED_DIR = PACKAGE_ROOT_DIR / "generated"

RIO_ASSETS_DIR = PACKAGE_ROOT_DIR / "assets"
HOSTED_ASSETS_DIR = RIO_ASSETS_DIR / "hosted"

SNIPPETS_DIR = PACKAGE_ROOT_DIR / "snippets" / "snippet-files"

if os.name == "nt":
    USER_CACHE_DIR = Path.home() / "AppData" / "Local" / "Cache"
    USER_CONFIG_DIR = Path.home() / "AppData" / "Roaming"
else:
    USER_CACHE_DIR = Path.home() / ".cache"
    USER_CONFIG_DIR = Path.home() / ".config"

RIO_CACHE_DIR = USER_CACHE_DIR / "rio"

RUNNING_IN_DEV_MODE = __debug__


_READONLY = object()
T = TypeVar("T")
Readonly = Annotated[T, _READONLY]


ImageLike = Union[Path, Image, URL, bytes]

MARKDOWN_ESCAPE = re.compile(r"([\\`\*_\{\}\[\]\(\)#\+\-.!])")
MARKDOWN_CODE_ESCAPE = re.compile(r"([\\`])")


def secure_string_hash(*values: str, hash_length: int = 32) -> str:
    """
    Returns a reproducible, secure hash for the given values.

    The order of values matters. In addition to the given values a global seed
    is added. This seed is generated once when the module is loaded, meaning the
    result is not suitable to be persisted across sessions.
    """

    hasher = hashlib.blake2b(
        _SECURE_HASH_SEED,
        digest_size=hash_length,
    )

    for value in values:
        hasher.update(value.encode("utf-8"))

    return hasher.hexdigest()


@dataclass(frozen=True)
class FileInfo:
    """
    Contains information about a file.

    When asking the user to select a file, this class is used to represent the
    file. It contains metadata about the file, and can also be used to access
    the file's contents.

    Be careful when running your app as a webserver, since files will need to be
    uploaded by the user, which is a potentially very slow operation.

    Attributes:
        name: The name of the file, including the extension.

        size_in_bytes: The size of the file, in bytes.

        media_type: The MIMe type of the file, such as `text/plain` or `image/png`.
    """

    name: str
    size_in_bytes: int
    media_type: str
    _contents: bytes

    async def read_bytes(self) -> bytes:
        """
        Asynchronously reads the entire file as `bytes`.

        Reads and returns the entire file as a `bytes` object. If you know that
        the file is text, consider using `read_text` instead.
        """
        return self._contents

    async def read_text(self, *, encoding: str = "utf-8") -> str:
        """
        Asynchronously reads the entire file as text.

        Reads and returns the entire file as a `str` object. The file is decoded
        using the given `encoding`. If you don't know that the file is valid
        text, use `read_bytes` instead.

        Args:
            encoding: The encoding to use when decoding the file.

        Raises:
            UnicodeDecodeError: The file could not be decoded using the given
                `encoding`.
        """
        return self._contents.decode(encoding)


T = TypeVar("T")
P = ParamSpec("P")

EventHandler = Optional[Callable[P, Union[Any, Awaitable[Any]]]]


def make_url_relative(base: URL, other: URL) -> URL:
    """
    Returns `other` as a relative URL to `base`. Raises a `ValueError` if
    `other` is not a child of `base`.

    This will never generate URLs containing `..`. If those would be needed a
    `ValueError` is raised.
    """
    # Verify the URLs have the same scheme and host
    if base.scheme != other.scheme:
        raise ValueError(
            f'URLs have different schemes: "{base.scheme}" and "{other.scheme}"'
        )

    if base.host != other.host:
        raise ValueError(f'URLs have different hosts: "{base.host}" and "{other.host}"')

    # Get the path segments of the URLs
    base_parts = base.parts
    other_parts = other.parts

    # Strip empty segments
    if base_parts and base_parts[-1] == "":
        base_parts = base_parts[:-1]

    if other_parts and other_parts[-1] == "":
        other_parts = other_parts[:-1]

    # See if the base is a parent of the other URL
    if base_parts != other_parts[: len(base_parts)]:
        raise ValueError(f'"{other}" is not a child of "{base}"')

    # Remove the common parts from the URL
    other_parts = other_parts[len(base_parts) :]
    return URL.build(
        path="/".join(other_parts),
        query=other.query,
        fragment=other.fragment,
    )


def escape_markdown(text: str) -> str:
    """
    Escape text such that it appears as-is when rendered as markdown.

    Given any text, this function returns a string which, when rendered as
    markdown, will look identical to the original text.
    """
    # TODO: Find a proper function for this. The current one is a total hack.
    return re.sub(MARKDOWN_ESCAPE, r"\\\1", text)


def escape_markdown_code(text: str) -> str:
    """
    Escape text such that it appears as-is inside a markdown code block.

    Given any text, this function returns a string which, when rendered inside
    a markdown code block, will look identical to the original text.
    """
    # TODO: Find a proper function for this. The current one is a total hack.
    return re.sub(MARKDOWN_CODE_ESCAPE, r"\\\1", text)
