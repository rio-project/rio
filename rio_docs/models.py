from dataclasses import dataclass
from typing import *  # type: ignore

import uniserde
from typing_extensions import Self

from . import parsers


@dataclass
class FunctionParameter(uniserde.Serde):
    name: str
    type: str | None
    default: str | None

    kw_only: bool

    collect_positional: bool
    collect_keyword: bool

    description: str | None


@dataclass
class FunctionDocs(uniserde.Serde):
    name: str
    parameters: list[FunctionParameter]
    return_type: str | None
    synchronous: bool

    short_description: str | None
    long_description: str | None

    raises: list[tuple[str, str]]  # type, description

    @classmethod
    def parse(cls, func: Callable) -> "FunctionDocs":
        return parsers.parse_function(func)


@dataclass
class ClassField(uniserde.Serde):
    name: str
    type: str
    default: str | None

    description: str | None


@dataclass
class ClassDocs(uniserde.Serde):
    name: str
    attributes: list[ClassField]  # name, type
    functions: list[FunctionDocs]

    short_description: str | None
    long_description: str | None

    @classmethod
    def parse(cls, typ: Type) -> "ClassDocs":
        return parsers.parse_class(typ)
