from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import *  # type: ignore

import reflex as rx

__all__ = [
    "AutoFormBuilder",
]


T = TypeVar("T")


@dataclass(frozen=True)
class FormField(Generic[T]):
    name: str
    type: Type[T]
    check: Optional[Callable[[T], Optional[str]]]


def prettify_name(name: str) -> str:
    parts = name.split("_")
    return " ".join(p.title() for p in parts)


class AutoFormBuilder:
    def __init__(
        self,
        fields: Iterable[FormField],
        check: Optional[Callable[[Dict[str, Any]], Optional[str]]] = None,
        *,
        spacing: float = 0.4,
    ):
        self.fields = tuple(fields)
        self.check = check
        self.spacing = spacing

    def _build_input_field(self, field: FormField) -> rx.Widget:
        origin = get_origin(field.type)
        args = get_args(field.type)

        # `bool` -> `Switch`
        if field.type is bool:
            return rx.Switch()

        # `int` -> `NumberInput`
        if field.type is int:
            raise NotImplementedError("TODO: Support `NumberInput`")

        # `float` -> `NumberInput`
        if field.type is float:
            raise NotImplementedError("TODO: Support `NumberInput`")

        # `str` -> `TextInput`
        if field.type is str:
            return rx.TextInput()

        # `Literal` or `Enum` -> `Dropdown`
        if origin is Literal or issubclass(field.type, enum.Enum):
            if origin is Literal:
                mapping = {a: a for a in args}
            else:
                mapping = {prettify_name(f.name): f.value for f in field.type}

            return rx.Dropdown(mapping)

        # Unsupported type
        raise TypeError(f"{__class__.__name__} does not support type `{field.type}`")

    def build(self) -> rx.Widget:
        rows: List[rx.Widget] = []

        # One row per field
        for field in self.fields:
            rows.append(
                rx.Row(
                    rx.Text(field.name),
                    self._build_input_field(field),
                    spacing=self.spacing,
                )
            )

        # Add a submit button
        rows.append(
            rx.Button.major(
                "Submit",
            )
        )

        # Wrap everything in one container
        return rx.Column(
            *rows,
            spacing=self.spacing,
        )
