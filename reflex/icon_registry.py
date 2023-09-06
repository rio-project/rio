import zipfile
from pathlib import Path
from typing import *  # type: ignore

from . import common
from .errors import AssetError

_icon_registry: Optional["IconRegistry"] = None


class IconRegistry:
    """
    Helper class, which keeps track of all icons known to reflex.

    Icons are stored in a zip file, and extracted on first use. Any icons which
    have been accessed are kept in memory for rapid access.
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir

        # Maps icon names (set/icon/variant) to the icon's SVG string. The icon
        # names are canonical form.
        self.cached_icons: Dict[str, str] = {}

        # Maps icon set names to the path of the zip file containing the icons
        self.icon_set_archives: Dict[str, Path] = {}

    @classmethod
    def get_singleton(cls) -> "IconRegistry":
        """
        Return the singleton instance of this class.
        """
        global _icon_registry

        # Create the instance if there is none yet
        if _icon_registry is None:
            _icon_registry = IconRegistry(
                common.REFLEX_CACHE_DIR / "extracted-icon-sets"
            )

        # Use it
        return _icon_registry

    @staticmethod
    def parse_icon_name(icon_name: str) -> Tuple[str, str, Optional[str]]:
        """
        Given a name for an icon, return the three parts of the name: set, icon,
        variant.If the name is syntactically invalid (e.g. too many slashes),
        raise an `AssetError`.
        """
        sections = icon_name.split("/")

        # Implicit set name
        if len(sections) == 1:
            return "material", icon_name, None

        # Too long
        if len(sections) > 3:
            raise AssetError(
                f"Invalid icon name `{icon_name}`. Icons names must be of the form `set/icon/variant`"
            )

        # Just right
        return tuple(sections)

    @staticmethod
    def normalize_icon_name(icon_name: str) -> str:
        """
        Given a name for an icon, return the canonical form of the name. If the
        name is syntactically invalid (e.g. too many slashes), raise an
        `AssetError`.
        """

        sections = IconRegistry.parse_icon_name(icon_name)

        if sections[2] is None:
            sections = sections[:2]

        return "/".join(sections)  # type: ignore

    def _get_icon_svg_path(
        self,
        icon_name: str,
    ) -> Path:
        """
        Given an icon name, return the path to the SVG file for that icon. This
        will extract the icon  if necessary.
        """
        # Prepare some paths
        icon_set, icon_name, variant = IconRegistry.parse_icon_name(icon_name)

        icon_set_dir = self.cache_dir / "extracted-icon-sets" / icon_set

        if variant is None:
            svg_path = icon_set_dir / f"{icon_name}.svg"
        else:
            svg_path = icon_set_dir / variant / f"{icon_name}.svg"

        # Check if the file has already been extracted
        if svg_path.exists():
            return svg_path

        # If the set's directory already exists there is nothing to do - this is
        # simply an invalid icon name
        if icon_set_dir.exists():
            return svg_path

        # If there is no icon set matching the name there is also nothing to do,
        # as this is an invalid / unregistered icon set
        try:
            zip_dir = self.icon_set_archives[icon_set]
        except KeyError:
            return svg_path

        # The cache directory doesn't exist. Extract the icon set's zip file to
        # create it
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_dir, "r") as zip_file:
            zip_file.extractall(self.cache_dir)

        return svg_path

    def get_icon_svg(self, icon_name: str) -> str:
        # Given an icon name, return the SVG string for that icon. This will
        # extract the icon if necessary. If the icon name is invalid or there is
        # no matching icon, raise an `AssetError`.

        # Normalize the icon name
        icon_name = IconRegistry.normalize_icon_name(icon_name)

        # Already cached?
        try:
            return self.cached_icons[icon_name]
        except KeyError:
            pass

        # Get the path to the icon's SVG file
        svg_path = self._get_icon_svg_path(icon_name)

        # Read the SVG file
        try:
            svg_string = svg_path.read_text()
        except FileNotFoundError:
            # Figure out which part of the name is the problem to show a
            # descriptive error message
            icon_set, icon_name, variant = IconRegistry.parse_icon_name(icon_name)

            icon_set_path = self.cache_dir / "extracted-icon-sets" / icon_set

            if not icon_set_path.exists():
                raise AssetError(
                    f"Unknown icon set `{icon_set}`. Known icon sets are: {', '.join(self.icon_set_archives.keys())}"
                )

            raise AssetError(
                f"There is no icon named `{icon_name}` in the `{icon_set}` icon set"
            )

        # Cache the icon
        self.cached_icons[icon_name] = svg_string

        # Done
        return svg_string
