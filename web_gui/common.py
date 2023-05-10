from typing import Dict, Tuple, Union, List
from pathlib import Path


PACKAGE_ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = PACKAGE_ROOT_DIR.parent / "frontend"
BUILD_DIR = PACKAGE_ROOT_DIR.parent / "build"


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
