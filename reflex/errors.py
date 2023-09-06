class NoFileSelectedError(Exception):
    pass


class AssetError(Exception):
    """
    Signifies that some operation related to assets has failed. E.g. trying to
    access a nonexistent asset.
    """

    def __init__(self, message: str):
        super().__init__(message)

    @property
    def message(self) -> str:
        return self.args[0]
