import inspect
from typing import *  # type: ignore

import rio

from . import article, articles

__all__ = [
    "DOCUMENTATION_STRUCTURE",
]


ArticleType: TypeAlias = Union[Tuple[str, str, Callable[[], article.Article]], Type]
SectionType: TypeAlias = Union[Tuple[str, Tuple[ArticleType, ...]], None]


# This acts as the source for anything that needs to know about the structure of
# the documentation. Other variables expose related information, but those
# variables derive from this one.
DOCUMENTATION_STRUCTURE: Tuple[SectionType, ...] = (
    # Introduction
    (
        "Getting Started",
        (
            (
                "First Steps",
                "first-steps",
                articles.first_steps.generate,
            ),
        ),
    ),
    None,
    # API Docs
    (
        "Inputs",
        (
            rio.Button,
            rio.TextInput,
        ),
    ),
    (
        "Layout",
        (
            rio.Row,
            rio.Column,
        ),
    ),
    (
        "Non-Widgets",
        (
            rio.App,
            rio.URL,
        ),
    ),
)


# Flattened view of `DOCUMENTATION_STRUCTURE`. This is a sequence of tuples:
#
# - URL Segment
# - Section Name
# - Article Name
# - Article generation function, or `Widget` class
def _compute_linear() -> (
    Tuple[
        Tuple[str, str, str, Union[Callable[[], article.Article], Type[rio.Widget]]],
        ...,
    ]
):
    result = []

    for section in DOCUMENTATION_STRUCTURE:
        # `None` is used to represent whitespace
        if section is None:
            continue

        # Otherwise, it's a tuple of (title, articles)
        section_title, arts = section

        # ... where each article is either a tuple of (name, url_segment,
        # article), or a rio `Widget`
        for art in arts:
            if isinstance(art, tuple):
                for art in arts:
                    name, url_segment, generate_article = art
                    result.append((url_segment, section_title, name, generate_article))

            else:
                assert inspect.isclass(art), art

                for art in arts:
                    name = art.__name__
                    result.append((name, section_title, name, art))

    return tuple(result)


DOCUMENTATION_STRUCTURE_LINEAR = _compute_linear()


# Maps URL segments to the sections they're in
def _compute_url_segment_to_section() -> Dict[str, str]:
    result = {}

    for url_segment, section_name, _, __ in DOCUMENTATION_STRUCTURE_LINEAR:
        result[url_segment] = section_name

    return result


DOCUMENTATION_URL_SEGMENT_TO_SECTION = _compute_url_segment_to_section()
