from pathlib import Path
from typing import Dict, List, Tuple, Union

PACKAGE_ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = PACKAGE_ROOT_DIR.parent / "frontend"


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
