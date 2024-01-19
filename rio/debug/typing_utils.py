import importlib
import types
from dataclasses import dataclass
from typing import Self

import introspection.typing

__all__ = ["ScopedAnnotation"]


@dataclass
class ScopedAnnotation:
    annotation: introspection.types.TypeAnnotation
    module: types.ModuleType

    def evaluate(self) -> introspection.types.TypeAnnotation:
        return introspection.typing.resolve_forward_refs(
            self.annotation,
            vars(self.module),
            mode="eval",
            strict=False,
            # Some modules are optional dependencies, so type annotations may
            # refer to modules/classes that aren't available. So if a name in
            # the global scope is missing, we'll try to import it.
            extra_globals=EXTRA_GLOBALS,
        )


class GlobalNamespace(dict):
    def __missing__(self, name: str) -> object:
        try:
            obj = importlib.import_module(name)
        except ImportError:
            obj = EmptyType

        self[name] = obj
        return obj


class EmptyTypeMeta(type):
    def __getattribute__(cls, attr: str) -> Self:
        return cls

    def __getitem__(cls, subtypes: object) -> Self:
        return cls


class EmptyType(metaclass=EmptyTypeMeta):
    """
    No object is an instance of this type. Used for type checking in place of
    classes that aren't available.
    """


EXTRA_GLOBALS = GlobalNamespace()
