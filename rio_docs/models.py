from dataclasses import dataclass
from typing import *  # type: ignore

import uniserde
from typing_extensions import Self

from . import parsers


@dataclass
class FunctionParameter(uniserde.Serde):
    name: str
    type: Optional[str]
    default: Optional[str]

    kw_only: bool

    collect_positional: bool
    collect_keyword: bool

    description: Optional[str]


@dataclass
class FunctionDocs(uniserde.Serde):
    name: str
    parameters: List[FunctionParameter]
    return_type: Optional[str]
    synchronous: bool

    short_description: Optional[str]
    long_description: Optional[str]

    raises: List[Tuple[str, str]]  # type, description

    @classmethod
    def parse(cls, func: Callable) -> "FunctionDocs":
        return parsers.parse_function(func)


@dataclass
class ClassField(uniserde.Serde):
    name: str
    type: str
    default: Optional[str]

    description: Optional[str]


@dataclass
class ClassDocs(uniserde.Serde):
    name: str
    attributes: List[ClassField]  # name, type
    functions: List[FunctionDocs]

    short_description: Optional[str]
    long_description: Optional[str]

    @classmethod
    def parse(cls, typ: Type) -> "ClassDocs":
        return parsers.parse_class(typ)
