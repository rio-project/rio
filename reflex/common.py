import hashlib
import inspect
import os
import secrets
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

from PIL.Image import Image
from typing_extensions import Annotated

_SECURE_HASH_SEED: bytes = secrets.token_bytes(32)

# Expose common paths on the filesystem
PACKAGE_ROOT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT_DIR = PACKAGE_ROOT_DIR.parent

GENERATED_DIR = PACKAGE_ROOT_DIR / "generated"

REFLEX_ASSETS_DIR = PACKAGE_ROOT_DIR / "assets"
HOSTED_ASSETS_DIR = REFLEX_ASSETS_DIR / "hosted"

if os.name == "nt":
    USER_CACHE_DIR = Path.home() / "AppData" / "Local" / "Cache"
    USER_CONFIG_DIR = Path.home() / "AppData" / "Roaming"
else:
    USER_CACHE_DIR = Path.home() / ".cache"
    USER_CONFIG_DIR = Path.home() / ".config"

REFLEX_CACHE_DIR = USER_CACHE_DIR / "reflex"


_READONLY = object()
T = TypeVar("T")
Readonly = Annotated[T, _READONLY]


Url = str
ImageLike = Union[Path, Image, Url, bytes]


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
    name: str
    size_in_bytes: int
    media_type: str
    _contents: bytes

    async def read_bytes(self) -> bytes:
        return self._contents

    async def read_text(self, *, encoding: str = "utf-8") -> str:
        return self._contents.decode(encoding)


T = TypeVar("T")
P = ParamSpec("P")

EventHandler = Optional[Callable[P, Any | Awaitable[Any]]]


@overload
async def call_event_handler(
    handler: EventHandler[[]],
) -> None:
    ...


@overload
async def call_event_handler(
    handler: EventHandler[[T]],
    event_data: T,
) -> None:
    ...


async def call_event_handler(  # type: ignore
    handler: EventHandler[P],
    *event_data: T,  # type: ignore
) -> None:
    """
    Call an event handler, if one is present. Await it if necessary. Log and
    discard any exceptions.
    """

    # Event handlers are optional
    if handler is None:
        return

    # If the handler is available, call it and await it if necessary
    try:
        result = handler(*event_data)  # type: ignore

        if inspect.isawaitable(result):
            await result

    # Display and discard exceptions
    except Exception:
        print("Exception in event handler:")
        traceback.print_exc()


def join_routes(base: Iterable[str], new: str) -> Tuple[str, ...]:
    """
    Given a base path and a new path, join them together and return the result.

    This will process any `./` and `../` parts in the new path, and return a
    list of path parts.

    Raises a `ValueError` if so many `../` are used that the route would leave
    the root route.

    Raises a `ValueError` if
    """

    # If the path is absolute (starts with '/'), ignore the base
    if new.startswith("/"):
        stack = []
        new = new[1:]
    else:
        stack = list(base)

    # Special case: Just '/'
    if not new:
        return tuple(stack)

    # Iterate through the parts of the path
    new_segments = new.split("/")
    for ii, segment in enumerate(new_segments):
        # Empty segments are acceptable only if they are the final segment,
        # since that just means the URL ended in a slash
        if not segment:
            if ii == len(new_segments) - 1:
                break

            raise ValueError(f"Route segments cannot be empty strings: `{new}`")

        # Nop
        if segment == ".":
            pass

        # One up
        elif segment == "..":
            try:
                stack.pop()
            except IndexError:
                base_str = "/" + "/".join(base)
                raise ValueError(
                    f"Route `{new}` would leave the root route when joined with `{base_str}`"
                )

        # Go to a child
        else:
            stack.append(segment)

    return tuple(stack)
