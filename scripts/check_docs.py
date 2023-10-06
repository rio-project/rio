"""
Helper script for running checks on documentation, such as looking for missing
docstrings.
"""


import inspect
from typing import *  # type: ignore

from revel import *  # type: ignore

import rio
import rio_docs
import website


def check_function(
    docs: rio_docs.FunctionDocs,
    owning_cls: Optional[Type],
) -> None:
    qualname = (
        f"{owning_cls.__name__}.{docs.name}" if owning_cls is not None else docs.name
    )

    # __init__ methods for components need no documentation, since the
    # class' documentation already fills that role
    if docs.name == "__init__" and owning_cls is not None and issubclass(owning_cls, rio.Component):  # type: ignore
        return

    # Fetch the docs
    if docs.short_description is None:
        warning(f"Docstring for `{qualname}` is missing a short description")

    if docs.long_description is None:
        warning(f"Docstring for `{qualname}` is missing a long description")


def check_class(cls: Type, docs: rio_docs.ClassDocs) -> None:
    # Run checks
    if docs.short_description is None:
        warning(f"Docstring for `{docs.name}` is missing a short description")

    if docs.long_description is None:
        warning(f"Docstring for `{docs.name}` is missing a long description")

    for attr in docs.attributes:
        if attr.description is None:
            warning(f"Docstring for `{docs.name}.{attr.name}` is missing a description")

    for func_docs in docs.functions:
        check_function(func_docs, cls)


def main() -> None:
    # Find all items that should be documented
    target_items: List[Union[Type, Callable]] = list(
        rio_docs.custom.find_items_needing_documentation()
    )

    # Make sure they're all properly documented
    for item in target_items:
        # Classes / Components
        if inspect.isclass(item):
            # Fetch the docs
            docs = rio_docs.ClassDocs.parse(item)

            # Post-process them as needed
            if isinstance(item, rio.Component):
                rio_docs.custom.postprocess_component_docs(docs)
            else:
                rio_docs.custom.postprocess_class_docs(docs)

            check_class(item, docs)

        else:
            assert inspect.isfunction(item), item

            docs = rio_docs.FunctionDocs.parse(item)

            check_function(docs, None)

    # Make sure all items are displayed Rio's documentation
    visited_item_names = set()

    for entry in website.structure.DOCUMENTATION_STRUCTURE_LINEAR:
        url, section_name, entry_name, art = entry
        visited_item_names.add(entry_name)

    for item in target_items:
        if item.__name__ not in visited_item_names:
            warning(f"Item `{item.__name__}` is not displayed in the documentation")


if __name__ == "__main__":
    main()
