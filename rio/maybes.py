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

if TYPE_CHECKING:
    import pandas
    import polars

_IS_INITIALIZED = False


# Maps numpy datatypes to a function which JSON-serializes them.
NUMPY_SERIALIZERS: Dict[Type, Callable[[Type], Any]] = {}

# If the libraries are available, these contain the DataFrame type
PANDAS_DATAFRAME_TYPES: Tuple[Type[pandas.DataFrame], ...] = ()
POLARS_DATAFRAME_TYPES: Tuple[Type[polars.DataFrame], ...] = ()


def initialize() -> None:
    """
    If called for the first time, initialize all constants in the module. This
    is not automatically done on module load, to make sure any needed modules
    have already been imported - some functionality is not initialized if those
    other modules aren't used.
    """
    global _IS_INITIALIZED, NUMPY_SERIALIZERS, PANDAS_DATAFRAME_TYPES, POLARS_DATAFRAME_TYPES

    # Already initialized?
    if _IS_INITIALIZED:
        return

    _IS_INITIALIZED = True

    # Is numpy available and loaded?
    if "numpy" in sys.modules:
        import numpy as np

        NUMPY_SERIALIZERS = {
            np.bool_: bool,
            np.uint8: int,
            np.uint16: int,
            np.uint32: int,
            np.uint64: int,
            np.int8: int,
            np.int16: int,
            np.int32: int,
            np.int64: int,
            np.float32: float,
            np.float64: float,
            np.str_: str,
        }

    if "pandas" in sys.modules:
        import pandas

        PANDAS_DATAFRAME_TYPES = (pandas.DataFrame,)

    if "polars" in sys.modules:
        import polars

        POLARS_DATAFRAME_TYPES = (polars.DataFrame,)
