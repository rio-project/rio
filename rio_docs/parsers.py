from __future__ import annotations

import dataclasses
import inspect
import re
import textwrap
from dataclasses import dataclass, is_dataclass
from typing import *  # type: ignore

import introspection.typing
from revel import *  # type: ignore

from rio.inspection import get_type_annotations

from . import models

# Maps common default factories to the value they represent
DEFAULT_FACTORY_VALUES: Dict[Any, Any] = {
    list: [],
    dict: {},
    set: set(),
    tuple: (),
}


def pre_parse_google_docstring(docstring: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Given a google-style docstring, return the description and sections.
    """
    description: str = ""
    sections: Dict[str, Dict[str, List[str]]] = {}

    current_section: Optional[Dict[str, List[str]]] = None
    current_lines: List[str] = []
    section_indent: int = 0

    # Trim the docstring
    docstring = textwrap.dedent(docstring.strip())

    # Process the docstring line by line
    lines = docstring.splitlines()

    for raw_line in lines:
        # Strip the line and calculate the indentation
        line = raw_line.lstrip()
        indent = len(raw_line) - len(line)
        line = line.rstrip()

        # Start of a new section
        if indent == 0 and line.endswith(":"):
            section_name = line[:-1]
            section_name = section_name.strip().lower()
            current_section = sections.setdefault(section_name, {})
            continue

        # If not inside a section, append to the description
        if current_section is None:
            description += line + "\n"
            continue

        # Check if the line contains a colon (:) to separate parameter name and description
        parts = line.split(":", 1)
        assert len(parts) >= 1, (line, parts)

        if len(parts) == 1:
            current_lines.append(parts[0].strip())
            continue

        if len(parts) == 2:
            name = parts[0].strip()
            value = parts[1].strip()
            current_lines = [value]
            current_section[name] = current_lines

    # Replace multiple empty lines with a single one
    description = re.sub("\n\n+", "\n\n", description)

    # Convert the section values from lists to strings
    result_sections: Dict[str, Dict[str, str]] = {}

    for section_name, section in sections.items():
        result_sections[section_name] = {}

        for name, lines in section.items():
            result_sections[section_name][name] = " ".join(lines)

    return description.strip(), result_sections


def parse_descriptions(description: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Given the description part of a docstring, split it into short and long
    descriptions. Either value may be Nonne if they are not present in the
    original string.
    """
    description = description.strip()

    # Split into short & long descriptions
    lines = description.split("\n")

    short_lines = []
    long_lines = []
    cur_lines = short_lines

    for line in lines:
        line = line.strip()

        cur_lines.append(line)

        if not line:
            cur_lines = long_lines

    # Join the lines
    short_description = "\n".join(short_lines).strip()
    long_description = "\n".join(long_lines).strip()

    if not short_description:
        short_description = None

    if not long_description:
        long_description = None

    # Done
    return short_description, long_description


def str_type_hint(typ: Type) -> str:
    # Make sure the type annotation has been parsed
    assert not isinstance(typ, str), typ

    # Then pretty-string the type
    return introspection.typing.annotation_to_string(typ)


def parse_docstring(
    docstring: str,
    *,
    enable_args: bool = False,
    enable_raises: bool = False,
    enable_attributes: bool = False,
) -> Tuple[Optional[str], Optional[str], Dict[str, Dict[str, str]]]:
    """
    Parses a docstring into

    - short description
    - long description
    - sections

    The function parameters control which sections are supported. Any other
    sections will trigger a warning and be removed. All enabled sections will be
    imputed (as empty) if they aren't present in the docstring. Sections are
    normalized to be lowercase.
    """

    # Pre-parse the docstring
    description, sections = pre_parse_google_docstring(docstring)

    # Parse the description
    short_description, long_description = parse_descriptions(description)

    # Post-process the sections
    enabled_sections = set()

    if enable_args:
        enabled_sections.add("args")

    if enable_raises:
        enabled_sections.add("raises")

    if enable_attributes:
        enabled_sections.add("attributes")

    for section_name in enabled_sections:
        sections.setdefault(section_name, {})

    for section in set(sections.keys()) - enabled_sections:
        warning(f"Removing superfluous section `{section}` from docstring")
        del sections[section]

    # Done
    return short_description, long_description, sections


def parse_function(func: Callable) -> models.FunctionDocs:
    """
    Given a function, parse its signature an docstring into a `FunctionDocs`
    object.
    """

    # Parse the parameters
    signature = inspect.signature(func)
    parameters: Dict[str, models.FunctionParameter] = {}

    for param_name, param in signature.parameters.items():
        if param.default == inspect.Parameter.empty:
            param_default = None
        else:
            param_default = repr(param.default)

        parameters[param_name] = models.FunctionParameter(
            name=param_name,
            type=None,  # Filled in later
            default=param_default,
            kw_only=param.kind == inspect.Parameter.KEYWORD_ONLY,
            collect_positional=param.kind == inspect.Parameter.VAR_POSITIONAL,
            collect_keyword=param.kind == inspect.Parameter.VAR_KEYWORD,
            description=None,
        )

    # Add the parameter types
    for param_name, param_type in get_type_hints(func).items():
        if param_name == "return":
            continue

        result_param = parameters[param_name]
        result_param.type = str_type_hint(param_type)

    # Parse the docstring
    docstring = inspect.getdoc(func)

    if docstring is None:
        short_description = None
        long_description = None
        raises = []
    else:
        short_description, long_description, sections = parse_docstring(
            docstring,
            enable_args=True,
            enable_raises=True,
        )

        raw_params = sections["args"]
        raw_raises = sections["raises"]

        # Add any information learned about parameters from the docstring
        for param_name, param_details in raw_params.items():
            try:
                result_param = parameters[param_name]
            except KeyError:
                warning(
                    f"The docstring for function `{func.__name__}` mentions a parameter `{param_name}` that does not exist in the function signature."
                )
                continue

            result_param.description = param_details

        # Add information about raised exceptions
        raises = list(raw_raises.items())

    # Build the result
    return models.FunctionDocs(
        name=func.__name__,
        parameters=list(parameters.values()),
        return_type=str_type_hint(get_type_hints(func).get("return", None)),
        short_description=short_description,
        long_description=long_description,
        raises=raises,
    )


def _parse_class_docstring_with_inheritance(
    cls: Type,
) -> Tuple[Optional[str], Optional[str], Dict[str, Dict[str, str]]]:
    """
    Parses the docstring of a class in the same format as `parse_docstring`, but
    accounts for inheritance: Sections of all classes are merged, in a way that
    preserves child docs over parent docs.
    """

    # Parse the docstring for this class
    raw_docs = inspect.getdoc(cls)
    docstring = parse_docstring(
        "" if raw_docs is None else raw_docs,
        enable_attributes=True,
    )

    # Get the docstrings for the base classes
    base_docs = []

    for base in cls.__bases__:
        base_docs.append(_parse_class_docstring_with_inheritance(base))

    # Merge the docstrings
    result_sections = {}
    all_in_order = base_docs + [docstring]

    for docs in all_in_order:
        for section_name, section in docs[2].items():
            result_section = result_sections.setdefault(section_name, {})
            result_section.update(section)

    # Done
    return docstring[0], docstring[1], result_sections


def parse_class(cls: Type) -> models.ClassDocs:
    """
    Given a class, parse its signature an docstring into a `ClassDocs` object.
    """

    # Parse the functions
    #
    # Make sure to add functions from base classes as well
    functions_by_name: Dict[str, models.FunctionDocs] = {}

    def add_functions(cls: Type) -> None:
        # Chain to the base classes
        for base in cls.__bases__:
            add_functions(base)

        # Then process this class. This way they override inherited functions.
        for name, func in inspect.getmembers(cls, inspect.isfunction):
            func_docs = parse_function(func)
            functions_by_name[name] = func_docs

    add_functions(cls)
    functions = list(functions_by_name.values())

    # Parse the fields
    fields_by_name: Dict[str, models.ClassField] = {}

    for name, typ in get_type_annotations(cls).items():
        if typ is dataclasses.KW_ONLY:
            continue

        fields_by_name[name] = models.ClassField(
            name=name,
            type=str_type_hint(typ),
            default=None,  # TODO
            description=None,  # TODO
        )

    # Is this a dataclass? If so, get the fields from there
    if is_dataclass(cls):
        for dataclass_field in dataclasses.fields(cls):
            doc_field = fields_by_name[dataclass_field.name]

            # Default value?
            if dataclass_field.default is not dataclasses.MISSING:
                doc_field.default = repr(dataclass_field.default)

            # Default factory?
            elif dataclass_field.default_factory is not dataclasses.MISSING:
                try:
                    default_value = DEFAULT_FACTORY_VALUES[
                        dataclass_field.default_factory
                    ]
                except KeyError:
                    pass
                else:
                    doc_field.default = repr(default_value)

    # Parse the docstring
    (
        short_description,
        long_description,
        sections,
    ) = _parse_class_docstring_with_inheritance(
        cls,
    )

    # Add any information learned about fields from the docstring
    raw_attributes = sections["attributes"]

    for field_name, field_details in raw_attributes.items():
        try:
            result_field = fields_by_name[field_name]
        except KeyError:
            warning(
                f"The docstring for class `{cls.__name__}` mentions a field `{field_name}` that does not exist in the class."
            )
            continue

        result_field.description = field_details

    # Treat properties as fields
    #
    # TODO

    # If this is a dataclass, the docs for the fields should also be used for
    # documenting parameters in `__init__`

    # Build the result
    return models.ClassDocs(
        name=cls.__name__,
        attributes=list(fields_by_name.values()),
        functions=functions,
        short_description=short_description,
        long_description=long_description,
    )
