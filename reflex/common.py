import enum
import hashlib
import inspect
import secrets
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

import fastapi
import uniserde
from typing_extensions import Annotated

_SECURE_HASH_SEED: bytes = secrets.token_bytes(32)


PACKAGE_ROOT_DIR = Path(__file__).resolve().parent
GENERATED_DIR = PACKAGE_ROOT_DIR / "generated"
HOSTED_ASSETS_DIR = PACKAGE_ROOT_DIR / "hosted-assets"


Jsonable: TypeAlias = uniserde.Jsonable


_READONLY = object()
T = TypeVar("T")
Readonly = Annotated[T, _READONLY]


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


class CursorStyle(enum.Enum):
    DEFAULT = enum.auto()
    POINTER = enum.auto()
