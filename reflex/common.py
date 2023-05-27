import hashlib
import os
import secrets
from pathlib import Path
from typing import Dict, List, Tuple, TypeVar, Union

from typing_extensions import Annotated

_SECURE_HASH_SEED: bytes = secrets.token_bytes(32)


PACKAGE_ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = PACKAGE_ROOT_DIR.parent / "frontend"


Jsonable = Union[
    None,
    bool,
    int,
    float,
    str,
    Tuple["Jsonable", ...],
    List["Jsonable"],
    Dict[str, "Jsonable"],
]

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
