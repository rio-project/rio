from dataclasses import dataclass
import uniserde
from typing import *  # type: ignore


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

    short_description: Optional[str]
    long_description: Optional[str]

    raises: List[Tuple[str, str]]  # type, description


@dataclass
class ClassField(uniserde.Serde):
    name: str
    type: str
    default: Optional[str]

    description: Optional[str]


@dataclass
class ClassDocs(uniserde.Serde):
    name: str
    fields: List[ClassField]  # name, type
    functions: List[FunctionDocs]

    short_description: Optional[str]
    long_description: Optional[str]
