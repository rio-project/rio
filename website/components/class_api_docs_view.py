from typing import *  # type: ignore

import reflex as rx
from reflex import escape_markdown as es
from reflex import escape_markdown_code as esc

from .. import models


def _str_parameter(param: models.FunctionParameter) -> str:
    parts = []

    # Name
    parts.append(param.name)

    # Type
    if param.type is not None:
        parts.append(f": {param.type}")

    # Default
    if param.default is not None:
        parts.append(f" = {param.default}")

    return "".join(parts)


def _str_function_signature(
    docs: models.FunctionDocs,
    *,
    owning_class_name: Optional[str] = None,
) -> str:
    parts = []

    # Name
    if owning_class_name is None:
        parts.append(f"def {docs.name}(")
    elif docs.name == "__init__":
        parts.append(f"{owning_class_name}(")
    else:
        parts.append(f"{owning_class_name}.{docs.name}(")

    # Parameters
    param_strs = [_str_parameter(param) for param in docs.parameters]

    # Multiline?
    if len(param_strs) == 0:
        pass

    elif len(param_strs) == 1:
        parts.append(param_strs[0])

    else:
        for param_str in param_strs:
            parts.append("\n    ")
            parts.append(esc(param_str))
            parts.append(", ")

        parts.append("\n")

    # Finish the parameter list
    parts.append(")")

    # Return type
    if docs.return_type is not None:
        parts.append(f" -> {esc(docs.return_type)}")

    return "".join(parts)


class ClassApiDocsView(rx.Widget):
    docs: models.ClassDocs

    def build(self) -> rx.Widget:
        parts = []

        # Header
        parts.append(f"# {self.docs.name}\n\n")

        # Short description
        if self.docs.short_description is not None:
            parts.append(f"{self.docs.short_description}\n\n")

        # Long description
        if self.docs.long_description is not None:
            parts.append(f"{self.docs.long_description}\n\n")

        # Fields
        parts.append("## Fields\n\n")

        if self.docs.fields:
            for field in self.docs.fields:
                parts.append(f"### {es(field.name)}\n\n")

                if field.description is not None:
                    parts.append(f"{field.description}\n\n")

                parts.append(f"Type: `{es(field.type)}`")

        else:
            parts.append(f"`{self.docs.name}` has no public fields.")

        parts.append("\n\n")

        # Functions
        parts.append("## Functions\n\n")

        if self.docs.functions:
            for fun in self.docs.functions:
                parts.append(f"### {es(fun.name)}\n\n")

                # Short description
                if fun.short_description is not None:
                    parts.append(f"{fun.short_description}\n\n")

                # Signature
                parts.append("```python\n")
                parts.append(
                    _str_function_signature(
                        fun,
                        owning_class_name=self.docs.name,
                    )
                )
                parts.append("\n```\n\n")

                # Long description
                if fun.long_description is not None:
                    parts.append(f"{fun.long_description}\n\n")

        # Events
        # TODO

        return rx.MarkdownView("".join(parts))
