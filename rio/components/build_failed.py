from .fundamental_component import FundamentalComponent

__all__ = ["BuildFailed"]


class BuildFailed(FundamentalComponent):
    """
    Used as a placeholder in case a component's `build` function throws an error.
    """


BuildFailed._unique_id = "BuildFailed-builtin"
