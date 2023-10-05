"""
Contains processing specific to the RIO project.
"""

from typing import *  # type: ignore

from revel import *  # type: ignore

from . import models


def postprocess_class_docs(docs: models.ClassDocs) -> None:
    """
    Perform RIO specific post-processing on the component, such as stripping out
    internal attributes and functions.
    """

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

        # No point in documenting somebody else's `build` method. It's not
        # supposed to be used by the user
        is_user_build_method = func.name == "build" and docs.name != "Component"
        keep = keep and not is_user_build_method

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
