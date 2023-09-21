from __future__ import annotations

import dataclasses
import inspect
from dataclasses import dataclass, is_dataclass
from typing import *  # type: ignore

import docstring_parser
import introspection.typing
from stream_tui import *  # type: ignore

from rio.inspection import get_type_annotations

from . import models

# Maps common default factories to the value they represent
DEFAULT_FACTORY_VALUES: Dict[Any, Any] = {
    list: [],
    dict: {},
    set: set(),
    tuple: (),
}


def str_type_hint(typ: Type) -> str:
    # Make sure the type annotation has been parsed
    assert not isinstance(typ, str), typ

    # Then pretty-string the type
    return introspection.typing.annotation_to_string(typ)


def parse_docstring(docstring: str) -> docstring_parser.Docstring:
    """
    Like `docstring_parser.parse`, but fixes some issues with that parser.
    """

    # Delegate to the original parser
    result = docstring_parser.parse(docstring)

    # It seems to simply consider the first line of the docstring as the short
    # description, even if there isn't a linebreak. This often cuts off the
    # first sentence.

    # Re-join the two descriptions
    description = ""

    if result.short_description is not None:
        description += result.short_description

    if result.long_description is not None:
        description += "\n" + result.long_description

    # Drop leading / trailing empty lines
    description = description.strip()

    # Find the first empty line
    lines = description.split("\n")

    for ii, line in enumerate(lines):
        if line.strip() == "":
            description_1 = ("\n".join(lines[:ii])).strip()
            description_2 = ("\n".join(lines[ii + 1 :])).strip()

    else:
        description_1 = description.strip()
        description_2 = None

        if len(description_1) > 100:
            description_2 = description_1
            description_1 = None

    # Update the result
    result.short_description = description_1
    result.long_description = description_2

    # Done
    return result


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
        docstring = parse_docstring(docstring)
        short_description = docstring.short_description
        long_description = docstring.long_description

        # Add any information learned about parameters from the docstring
        for docstring_param in docstring.params:
            try:
                result_param = parameters[docstring_param.arg_name]
            except KeyError:
                warning(
                    f"The docstring for function `{func.__name__}` mentions a parameter `{docstring_param.arg_name}` that does not exist in the function signature."
                )
                continue

            result_param.description = docstring_param.description

        # Add information about raised exceptions
        raises = []

        for docstring_raise in docstring.raises:
            raises.append((docstring_raise.type_name, docstring_raise.description))

    # Build the result
    return models.FunctionDocs(
        name=func.__name__,
        parameters=list(parameters.values()),
        return_type=str_type_hint(get_type_hints(func).get("return", None)),
        short_description=short_description,
        long_description=long_description,
        raises=raises,
    )


def parse_class(cls: Type) -> models.ClassDocs:
    """
    Given a class, parse its signature an docstring into a `ClassDocs` object.
    """

    # Parse the functions
    functions = []

    for name, func in inspect.getmembers(cls, inspect.isfunction):
        functions.append(parse_function(func))

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
    docstring = inspect.getdoc(cls)

    if docstring is None:
        short_description = None
        long_description = None

    else:
        docstring = parse_docstring(docstring)
        short_description = docstring.short_description
        long_description = docstring.long_description

        # Add any information learned about fields from the docstring
        #
        # TODO: Can docstrings contain field information?

    # Treat properties as fields
    #
    # TODO

    # If this is a dataclass, the docs for the fields should also be used for
    # documenting parameters in `__init__`

    # Build the result
    return models.ClassDocs(
        name=cls.__name__,
        fields=list(fields_by_name.values()),
        functions=functions,
        short_description=short_description,
        long_description=long_description,
    )
