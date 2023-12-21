import logging
import zipfile
from pathlib import Path
from typing import *  # type: ignore

from . import common
from .errors import AssetError

_icon_registry: Optional["IconRegistry"] = None


class IconRegistry:
    """
    Helper class, which keeps track of all icons known to rio.

    Icons are stored in a zip file, and extracted on first use. Any icons which
    have been accessed are kept in memory for rapid access.
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir

        # Maps icon names (set/icon:variant) to the icon's SVG string. The icon
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
            _icon_registry = IconRegistry(common.RIO_CACHE_DIR / "extracted-icon-sets")

            # Register built-in icon sets
            _icon_registry.icon_set_archives["material"] = (
                common.RIO_ASSETS_DIR / "compressed-icon-sets" / "material.zip"
            )

        # Use it
        return _icon_registry

    @staticmethod
    def parse_icon_name(icon_name: str) -> Tuple[str, str, Optional[str]]:
        """
        Given a name for an icon, return the three parts of the name: set, icon,
        variant. If the name is syntactically invalid (e.g. too many slashes),
        raise an `AssetError`.
        """
        # Determine the icon set
        sections = icon_name.split("/")

        if len(sections) == 1:
            icon_set = "material"
            icon_name = sections[0]
        elif len(sections) == 2:
            icon_set, icon_name = sections
        else:
            raise AssetError(
                f"Invalid icon name `{icon_name}`. Icons names must be of the form `set/icon:variant`"
            )

        # Determine the icon name and variant
        sections = icon_name.split(":")

        if len(sections) == 1:
            return icon_set, sections[0], None

        if len(sections) == 2:
            return icon_set, sections[0], sections[1]

        raise AssetError(
            f"Invalid icon name `{icon_name}`. Icons names must be of the form `set/icon:variant`"
        )

    @staticmethod
    def normalize_icon_name(icon_name: str) -> str:
        """
        Given a name for an icon, return the canonical form of the name. If the
        name is syntactically invalid (e.g. too many slashes), raise an
        `AssetError`.
        """

        set, name, section = IconRegistry.parse_icon_name(icon_name)

        if section is None:
            return f"{set}/{name}"

        return f"{set}/{name}:{section}"

    def _ensure_icon_set_is_extracted(self, icon_set: str) -> None:
        """
        Given the name of an icon set, extract the icon set's zip file to the
        cache directory. The target director must not exist yet. Raises a
        `KeyError` if no icon set with the given name has been registered.
        """
        # If the target directory already exists there is nothing to do
        target_dir = self.cache_dir / icon_set

        if target_dir.exists():
            return

        # Get the path to the icon set's zip file. If there is no icon set with
        # the given name, this will raise a `KeyError`. That's fine.
        archive_path = self.icon_set_archives[icon_set]

        # Extract the set
        target_dir.mkdir(parents=True, exist_ok=True)

        logging.debug(
            f"Extracting icon set `{icon_set}` from `{archive_path}` to `{target_dir}`"
        )

        with zipfile.ZipFile(archive_path, "r") as zip_file:
            zip_file.extractall(target_dir)

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

        icon_set_dir = self.cache_dir / icon_set

        if variant is None:
            svg_path = icon_set_dir / f"{icon_name}.svg"
        else:
            svg_path = icon_set_dir / variant / f"{icon_name}.svg"

        # Extract the icon set if necessary
        self._ensure_icon_set_is_extracted(icon_set)

        return svg_path

    def get_icon_svg(self, icon_name: str) -> str:
        """
        Given an icon name, return the SVG string for that icon. This will
        extract the icon if necessary. If the icon name is invalid or there is
        no matching icon, raise an `AssetError`.
        """

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

            icon_set_path = self.cache_dir / icon_set

            if not icon_set_path.exists():
                raise AssetError(
                    f"Unknown icon set `{icon_set}`. Known icon sets are: `{'`, `'.join(self.icon_set_archives.keys())}`"
                )

            raise AssetError(
                f"There is no icon named `{icon_name}` in the `{icon_set}` icon set"
            )

        # Cache the icon
        self.cached_icons[icon_name] = svg_string

        # Done
        return svg_string

    def _get_variant_directories(
        self, icon_set: str
    ) -> Iterable[Tuple[Optional[str], Path]]:
        """
        Given the name of an icon set, list the names of all variants in that
        set along with the directory they are stored in.
        """

        # Make sure the icon set is extracted
        self._ensure_icon_set_is_extracted(icon_set)

        # Iterate over all files in the icon set directory. Directories
        # correspond to variants. If icons are found in the root directory, they
        # are part of the default variant.
        icon_set_dir = self.cache_dir / icon_set
        has_default_variant = False

        for path in icon_set_dir.iterdir():
            if path.is_dir():
                yield (path.name, path)
            else:
                has_default_variant = True

        if has_default_variant:
            yield (None, icon_set_dir)

    def all_icon_sets(self) -> Iterable[str]:
        """
        Return the names of all icon set names known to rio.
        """
        return self.icon_set_archives.keys()

    def all_variants_in_set(self, icon_set: str) -> Iterable[Optional[str]]:
        """
        Given the name of an icon set, list the names of all variants in that
        set.
        """
        for name, _ in self._get_variant_directories(icon_set):
            yield name

    def all_icons_in_set(
        self,
        icon_set: str,
        *,
        variant: Optional[str] = None,
    ) -> Iterable[Tuple[str, Optional[str]]]:
        """
        Given the name of an icon set, list all icon names and variants in that
        set. If `variant` is given, only return icons with that variant.
        Otherwise, icons of all variants are returned.

        Raises a `KeyError` if there is not icon set or variant with the given
        name.
        """
        # Find all available variants. This will also extract the icon set if
        # necessary.
        variants = dict(self._get_variant_directories(icon_set))

        # Apply the variant filter. Any `KeyError` is propagated.
        if variant is not None:
            variants = {variant: variants[variant]}

        # Iterate over all variants
        for variant_name, path in variants.items():
            for icon_path in path.iterdir():
                # Only care for SVG files
                if icon_path.is_dir() or icon_path.suffix != ".svg":
                    continue

                # Yield
                icon_name = icon_path.stem
                yield icon_name, variant_name
