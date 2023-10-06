"""
Contains helpers for creating articles on the website. Articles are represented
as sequences of `Union[rio.Component, str]`. Strings are rendered as markdown.
"""

from typing import *  # type: ignore

import rio
from rio import escape_markdown as es
from rio import escape_markdown_code as esc
from rio_docs import models as docmodels

from . import components as comps
from . import theme


class Article:
    def __init__(
        self,
        *,
        default_language: Optional[str] = "python",
    ):
        self.default_language = default_language

        self._parts: List[rio.Component] = []
        self._current_section: Optional[List[rio.Component]] = None

    def begin_section(self) -> None:
        if self._current_section is not None:
            raise ValueError(f"This article is already in a section")

        self._current_section = []

    def end_section(self) -> None:
        if self._current_section is None:
            raise ValueError(f"This article is not currently in a section")

        self._parts.append(rio.Card(rio.Column(*self._current_section)))
        self._current_section = None

    def component(self, component: rio.Component) -> None:
        if self._current_section is None:
            self._parts.append(component)
        else:
            self._current_section.append(component)

    def spacer(self, height: float) -> None:
        self.component(rio.Spacer(height=height))

    def text(
        self,
        text: str,
        *,
        style: Union[
            Literal["heading1", "heading2", "heading3", "text"],
            rio.TextStyle,
        ] = "text",
    ) -> None:
        self.component(
            rio.Text(
                text,
                style=style,
                # Match the alignment of `MarkdownView`
                align_x=None if style == "text" else 0,
            )
        )

    def markdown(self, text: str) -> None:
        self.component(
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

        # Build the component
        self.markdown(markdown)

    def build(self) -> rio.Component:
        return rio.Column(
            *self._parts,
            spacing=4,
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

    # TODO: Don't forget the * and **, both for variadic parameters, and for
    #       positional-/keyword-only parameters

    # Name
    if owning_class_name is None:
        parts.append("def " if docs.synchronous else "async def ")
        parts.append(docs.name)
        parts.append("(")
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


def _append_method_docs_to_article(
    art: Article,
    docs: docmodels.ClassDocs,
    *,
    filter: Callable[[docmodels.FunctionDocs], bool] = lambda _: True,
) -> None:
    # Find all methods to document
    targets = [func for func in docs.functions if filter(func)]

    # Are there any methods to document?
    if not targets:
        return

    # Document them
    art.begin_section()
    art.text("Functions", style="heading2")

    for func in targets:
        # Heading
        art.spacer(1)
        art.text(f"{docs.name}.{func.name}", style="heading3")

        # Signature
        art.code_block(_str_function_signature(func))

        # Short description
        if func.short_description is not None:
            art.markdown(func.short_description)

        # Long description
        if func.long_description is not None:
            art.markdown(func.long_description)

        # Parameters
        for param in func.parameters:
            if param.name == "self":
                continue

            art.component(
                rio.Row(
                    rio.Text(
                        param.name,
                        style="heading3",
                    ),
                    rio.MarkdownView(
                        "Unknown" if param.type is None else f"`{esc(param.type)}`",
                        margin_left=1.0,
                        default_language="python",
                    ),
                    rio.Spacer(),
                ),
            )

            if param.description is not None:
                art.markdown(param.description)

    art.end_section()


def _append_field_docs_to_article(
    art: Article,
    docs: docmodels.ClassDocs,
) -> None:
    # Are there any fields to document?
    if not docs.attributes:
        return

    art.begin_section()
    art.text("Attributes", style="heading2")

    for field in docs.attributes:
        art.component(
            rio.Row(
                rio.Text(
                    field.name,
                    style="heading3",
                ),
                rio.MarkdownView(
                    f"`{esc(field.type)}`",
                    margin_left=1.0,
                    default_language="python",
                ),
                rio.Spacer(),
            ),
        )

        if field.description is not None:
            art.markdown(field.description)

    art.end_section()


def _append_heading_and_short_description(
    art: Article,
    heading: str,
    short_description: Optional[str],
) -> None:
    art.component(
        rio.Row(
            rio.Card(
                child=rio.Column(
                    rio.Text(
                        heading,
                        style="heading1",
                        align_x=0,
                    ),
                    rio.MarkdownView(
                        short_description or "",
                        default_language="python",
                    ),
                    align_y=0,
                    margin=2,
                ),
                width="grow",
                corner_radius=theme.THEME.corner_radius_large,
            ),
            rio.Image(
                theme.get_random_material_image(),
                width="grow",
                corner_radius=theme.THEME.corner_radius_large,
                fill_mode="zoom",
            ),
            spacing=2,
            height=20,
        )
    )


def create_class_api_docs(docs: docmodels.ClassDocs) -> Article:
    art = Article()

    # Heading / short description
    _append_heading_and_short_description(
        art,
        docs.name,
        docs.short_description,
    )

    # Long description
    if docs.long_description is not None:
        art.markdown(docs.long_description)

    # Fields
    _append_field_docs_to_article(art, docs)

    # Functions
    _append_method_docs_to_article(art, docs)

    # Events
    # TODO

    # Done
    return art


def create_component_api_docs(
    docs: docmodels.ClassDocs,
    interactive_example: Optional[Callable[[], rio.Component]],
) -> Article:
    art = Article()

    # Heading / short description
    _append_heading_and_short_description(
        art,
        docs.name,
        docs.short_description,
    )

    # Constructor Signature
    for init_function in docs.functions:
        if init_function.name == "__init__":
            break
    else:
        raise ValueError(f"Could not find constructor for component `{docs.name}`")

    init_signature = _str_function_signature(
        init_function,
        owning_class_name=docs.name,
    )
    art.code_block(init_signature)

    # Details
    if docs.long_description is not None:
        art.markdown(docs.long_description)

    # Interactive example
    if interactive_example is not None:
        art.component(interactive_example())

    # Attributes / Constructor arguments
    #
    # These are merged into a single section, because developers are unlikely to
    # interact with the attributes anywhere but the constructor.
    _append_field_docs_to_article(art, docs)

    # Functions
    _append_method_docs_to_article(
        art,
        docs,
        filter=lambda func: func.name != "__init__",
    )

    return art
