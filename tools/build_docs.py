import inspect
from dataclasses import dataclass
from typing import *  # type: ignore

import docstring_parser
from stream_tui import *  # type: ignore

from website.models import ClassDocs, ClassField, FunctionDocs, FunctionParameter


def str_type_hint(typ: Type) -> str:
    # TODO: Take care of origin/args
    # Display unions as a | b
    # Add / Strip qualifiers
    # Normalize list / List & Co

    if isinstance(typ, str):
        return typ

    return typ.__name__


def parse_function(func: Callable) -> FunctionDocs:
    """
    Given a function, parse its signature an docstring into a `FunctionDocs`
    object.
    """

    # Parse the parameters
    signature = inspect.signature(func)
    parameters: Dict[str, FunctionParameter] = {}

    for param_name, param in signature.parameters.items():
        if param.annotation == inspect.Parameter.empty:
            param_type = None
        else:
            param_type = param.annotation

        if param.default == inspect.Parameter.empty:
            param_default = None
        else:
            param_default = repr(param.default)

        parameters[param_name] = FunctionParameter(
            name=param_name,
            type=None if param_type is None else param_type,
            default=param_default,
            kw_only=param.kind == inspect.Parameter.KEYWORD_ONLY,
            collect_positional=param.kind == inspect.Parameter.VAR_POSITIONAL,
            collect_keyword=param.kind == inspect.Parameter.VAR_KEYWORD,
            description=None,
        )

    # Parse the docstring
    docstring = inspect.getdoc(func)
    if docstring is None:
        short_description = None
        long_description = None
        raises = []
    else:
        docstring = docstring_parser.parse(docstring)
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
    return FunctionDocs(
        name=func.__name__,
        parameters=list(parameters.values()),
        return_type=str_type_hint(signature.return_annotation),
        short_description=short_description,
        long_description=long_description,
        raises=raises,
    )


def parse_class(cls: Type) -> ClassDocs:
    """
    Given a class, parse its signature an docstring into a `ClassDocs` object.
    """

    # Parse the functions
    functions = []

    for name, func in inspect.getmembers(cls, inspect.isfunction):
        functions.append(parse_function(func))

    # Build the result
    return ClassDocs(
        name=cls.__name__,
        fields=[],
        functions=functions,
        short_description=None,
        long_description=None,
    )
