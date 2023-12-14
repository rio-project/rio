"""
This module exposes functionality which may or may not exist, depending on which
modules are available on the system.

Some values are not initialized at all, if the required module isn't in
`sys.modules`. This avoids long startup times if modules are available but not
used.
"""

from __future__ import annotations

import sys
from typing import *  # type: ignore

import introspection

if TYPE_CHECKING:
    import pandas
    import polars

_IS_INITIALIZED = False


T = TypeVar("T")


FLOAT_TYPES = (float, int)
INT_TYPES = (int,)
BOOL_TYPES = (bool,)
STR_TYPES = (str,)

PANDAS_DATAFRAME_TYPES: Tuple[Type[pandas.DataFrame], ...] = ()
POLARS_DATAFRAME_TYPES: Tuple[Type[polars.DataFrame], ...] = ()

# This is a mapping of "weird" types to the "canonical" type, like `{np.int8: int}`
TYPE_NORMALIZERS: Mapping[Type[T], Callable[[T], T]] = {}  # type: ignore


def initialize() -> None:
    """
    If called for the first time, initialize all constants in the module. This
    is not automatically done on module load, to make sure any needed modules
    have already been imported - some functionality is not initialized if those
    other modules aren't used.
    """
    global _IS_INITIALIZED
    global FLOAT_TYPES, INT_TYPES, BOOL_TYPES, STR_TYPES
    global PANDAS_DATAFRAME_TYPES, POLARS_DATAFRAME_TYPES

    # Already initialized?
    if _IS_INITIALIZED:
        return

    _IS_INITIALIZED = True

    # Is numpy available and loaded?
    if "numpy" in sys.modules:
        import numpy

        numpy_floats = tuple(introspection.iter_subclasses(numpy.floating))
        numpy_ints = tuple(introspection.iter_subclasses(numpy.integer))
        numpy_bools = tuple(introspection.iter_subclasses(numpy.bool_))
        numpy_strings = tuple(introspection.iter_subclasses(numpy.str_))

        FLOAT_TYPES = (*FLOAT_TYPES, *numpy_floats, *numpy_ints)
        INT_TYPES += numpy_ints
        BOOL_TYPES += numpy_bools
        STR_TYPES += numpy_strings

    if "pandas" in sys.modules:
        import pandas

        PANDAS_DATAFRAME_TYPES = (pandas.DataFrame,)

    if "polars" in sys.modules:
        import polars

        POLARS_DATAFRAME_TYPES = (polars.DataFrame,)

    # Populate our mapping of type normalizers
    for canonical_type, weird_types in (
        (str, STR_TYPES),
        (bool, BOOL_TYPES),
        (int, INT_TYPES),
        (float, FLOAT_TYPES),
    ):
        for weird_type in weird_types:
            TYPE_NORMALIZERS[weird_type] = canonical_type
