"""
Contains helpers for creating articles on the website. Articles are represented
as sequences of `Union[rio.Widget, str]`. Strings are rendered as markdown.
"""

from typing import *  # type: ignore

import rio
from rio import escape_markdown as es
from rio import escape_markdown_code as esc
from rio_docs import models as docmodels

from . import components as comps


class Article:
    def __init__(
        self,
        *,
        default_language: Optional[str] = "python",
    ):
        self.default_language = default_language

        self._parts: List[rio.Widget] = []
        self._current_section: Optional[List[rio.Widget]] = None

    def begin_section(self) -> None:
        if self._current_section is not None:
            raise ValueError(f"This article is already in a section")

        self._current_section = []

    def end_section(self) -> None:
        if self._current_section is None:
            raise ValueError(f"This article is not currently in a section")

        self._parts.append(comps.FlatCard(rio.Column(*self._current_section)))
        self._current_section = None

    def widget(self, widget: rio.Widget) -> None:
        if self._current_section is None:
            self._parts.append(widget)
        else:
            self._current_section.append(widget)

    def text(
        self,
        text: str,
        *,
        style: Union[
            Literal["heading1", "heading2", "heading3", "text"],
            rio.TextStyle,
        ] = "text",
    ) -> None:
        self.widget(
            rio.Text(
                text,
                style=style,
                # Match the alignment of `MarkdownView`
                align_x=None if style == "text" else 0,
            )
        )

    def markdown(self, text: str) -> None:
        self.widget(
            rio.MarkdownView(
                text,
                default_language=self.default_language,
            )
        )

    def code_block(self, code: str) -> None:
        # Header
        markdown = "```"

        if self.default_language is not None:
            markdown += self.default_language

        markdown += "\n"

        # Code
        markdown += esc(code)

        # Footer
        markdown += "\n```"

        # Build the widget
        self.markdown(markdown)

    def build(self) -> rio.Widget:
        return rio.Column(
            *self._parts,
            spacing=2,
        )


def _str_parameter(param: docmodels.FunctionParameter) -> str:
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
    docs: docmodels.FunctionDocs,
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


def create_class_api_docs(docs: docmodels.ClassDocs) -> Article:
    art = Article()

    # Heading
    art.begin_section()
    art.text(docs.name, style="heading1")

    # Short description
    if docs.short_description is not None:
        art.markdown(docs.short_description)

    # Long description
    if docs.long_description is not None:
        art.markdown(docs.long_description)

    # Fields
    art.text("Fields", style="heading2")

    if docs.attributes:
        for field in docs.attributes:
            art.text(es(field.name), style="heading3")

            if field.description is not None:
                art.markdown(field.description)

            art.markdown(f"Type: `{esc(field.type)}`\n\n")

    else:
        art.markdown(f"`{esc(docs.name)}` has no public fields.")

    rio.Spacer(height=1.5)

    # Functions
    art.text("Functions", style="heading2")

    if docs.functions:
        for fun in docs.functions:
            art.text(es(fun.name), style="heading3")

            # Short description
            if fun.short_description is not None:
                art.markdown(fun.short_description)

            # Signature
            art.code_block(_str_function_signature(fun, owning_class_name=docs.name))

            # Long description
            if fun.long_description is not None:
                art.markdown(fun.long_description)

    # Events
    # TODO

    # Done
    art.end_section()
    return art


def create_widget_api_docs(
    docs: docmodels.ClassDocs,
    interactive_example: Optional[Callable[[], rio.Widget]],
) -> Article:
    art = Article()

    # Heading
    art.begin_section()
    art.text(docs.name, style="heading1")

    # Short description
    if docs.short_description is not None:
        art.markdown(docs.short_description)

    # Constructor Signature
    for init_function in docs.functions:
        if init_function.name == "__init__":
            break
    else:
        raise ValueError(f"Could not find constructor for widget `{docs.name}`")

    init_signature = _str_function_signature(
        init_function,
        owning_class_name=docs.name,
    )
    art.code_block(init_signature)

    # Attributes / Constructor arguments
    #
    # These are merged into a single section, because developers are unlikely to
    # interact with the attributes anywhere but the constructor.

    for field in docs.attributes:
        art.widget(
            rio.Row(
                rio.Text(
                    field.name,
                    style="heading3",
                ),
                rio.MarkdownView(
                    f"`{esc(field.type)}`",
                    margin_left=0.5,
                ),
                rio.Spacer(),
            ),
        )

        if field.description is not None:
            art.markdown(field.description)

    art.end_section()

    # Interactive example
    if interactive_example is not None:
        art.widget(interactive_example())

    # Details
    art.begin_section()
    art.text("Details", style="heading2")

    if docs.long_description is not None:
        art.markdown(docs.long_description)

    art.end_section()

    # Functions
    if docs.functions:
        art.begin_section()
        art.text("Functions", style="heading2")

        for func in docs.functions:
            # Skip the constructor, as it was already handled above
            if func.name == "__init__":
                continue

            # Heading
            art.text(func.name, style="heading3")

            # Signature
            art.code_block(_str_function_signature(func, owning_class_name=docs.name))

            # Short description
            if func.short_description is not None:
                art.markdown(func.short_description)

            # Long description
            if func.long_description is not None:
                art.markdown(func.long_description)

        art.end_section()

    return art