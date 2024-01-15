import importlib
import sys
import types

__all__ = ["ModuleProxy"]


class ModuleProxy:
    """
    Some modules are optional dependencies and only imported behind a `if
    TYPE_CHECKING:` guard. But when running in debug mode, runtime type checking
    will be enabled, so we need access to those modules. That's where this class
    comes in: It lazily imports a module only when it's necessary.

    Usage example:

        if TYPE_CHECKING:
            import plotly.figure
        else:
            plotly = ModuleProxy('plotly.figure')
    """

    def __init__(self, module_name: str):
        self.__module: types.ModuleType | None = None
        self.__module_name = module_name

    def __getattr__(self, attr: str) -> object:
        if self.__module is None:
            importlib.import_module(self.__module_name)

            root_module, _, _ = self.__module_name.partition(".")
            self.__module = sys.modules[root_module]

        return getattr(self.__module, attr)
