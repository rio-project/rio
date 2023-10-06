"""
Contains processing specific to the RIO project.
"""

from typing import *  # type: ignore

from revel import *  # type: ignore

import rio

from . import models


def find_items_needing_documentation() -> Iterable[Union[Type, Callable]]:
    """
    Find all classes and functions in `Rio` that need to be documented.
    """

    # Hardcoded items
    yield rio.App
    yield rio.AssetError
    yield rio.BoxStyle
    yield rio.Color
    yield rio.CursorStyle
    yield rio.Font
    yield rio.NavigationFailed
    yield rio.Page
    yield rio.Session
    yield rio.TextStyle
    yield rio.Theme
    yield rio.UserSettings

    # Yield classes that also need their children documented
    to_do = [
        rio.Fill,
        rio.Component,
    ]

    while to_do:
        cur = to_do.pop()

        # Hardcoded items that DON'T need documentation
        if cur.__name__ in (
            "ClassContainer",
            "FundamentalComponent",
            "RootContainer",
        ):
            continue

        # Skip anything not in the `rio` module
        if not cur.__module__.startswith("rio"):
            continue

        # Internal
        if not cur.__name__.startswith("_"):
            yield cur

        # Found one
        to_do.extend(cur.__subclasses__())


def postprocess_class_docs(docs: models.ClassDocs) -> None:
    """
    Perform RIO specific post-processing on the component, such as stripping out
    internal attributes and functions.
    """

    # Strip default docstrings created by dataclasses
    if docs.short_description is not None and docs.short_description.startswith(
        f"{docs.name}("
    ):
        docs.short_description = None
        docs.long_description = None

    # Strip internal attributes
    index = 0
    while index < len(docs.attributes):
        attr = docs.attributes[index]

        # Decide whether to keep it
        keep = not attr.name.startswith("_")

        # Strip it out, if necessary
        if keep:
            index += 1
        else:
            del docs.attributes[index]

    # Skip internal functions
    index = 0
    while index < len(docs.functions):
        func = docs.functions[index]

        # Decide whether to keep it

        # Internal methods start with an underscore
        keep = not func.name.startswith("_")

        # Some methods in components are meant to be used by the user, but only
        # when they're the one creating the component. For example, the `build`
        # method is only intended to be used by the widget itself, and
        # documenting it would be pointless at best, and confusing at worst.
        is_inherited_protected_method = docs.name != "Component" and func.name in (
            "build",
            "call_event_handler",
            "force_refresh",
        )
        keep = keep and not is_inherited_protected_method

        # Strip lambdas
        keep = keep and func.name != "<lambda>"

        # Make sure to keep the constructor
        keep = keep or func.name == "__init__"

        # Strip it out, if necessary
        if keep:
            index += 1
        else:
            del docs.functions[index]


def postprocess_component_docs(docs: models.ClassDocs) -> None:
    return postprocess_class_docs(docs)
