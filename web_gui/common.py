from typing import Dict, Tuple, Union, List

Jsonable = Union[
    None,
    bool,
    int,
    float,
    str,
    Tuple["Jsonable", ...],
    List["Jsonable"],
    Dict[str, "Jsonable"],
]
