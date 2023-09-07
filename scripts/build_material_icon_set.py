"""
This file reads all materials icons/symbols from their github repository and
packs them into a zip file that can be used by reflex as icon set.
"""

import re
import tempfile
import zipfile
from pathlib import Path
from typing import *  # type: ignore
from xml.etree import ElementTree as ET

from stream_tui import *  # type: ignore

import reflex as rx

# Configure: The name the resulting icon set will have
SET_NAME = "material"

# Configure: The path to the directory which should be scanned for SVG files.
#
# Repo URL: https://github.com/marella/material-symbols
INPUT_DIR = (
    rx.common.PROJECT_ROOT_DIR
    / "thirdparty"
    / "material-symbols"
    / "svg"
    / "500"
    / "rounded"
)

# Configure: Any files in the input directory which match this pattern will be
# processed
INPUT_NAME_PATTERN = r"(.+).svg"

# Configure: (.+).svg"The output file will be written into this directory as
# <SET_NAME>.zip
OUTPUT_DIR = rx.common.REFLEX_ASSETS_DIR / "compressed-icon-sets"

# For debugging: Stop after processing this many icons. Set to `None` for no
# limit
LIMIT = None


# Configure: Given the relative path to the icon, return the icon's name and
# optionally variant.
#
# If `None` is returned the file is skipped.
def name_from_icon_path(path: Path) -> Optional[Tuple[str, Optional[str]]]:
    # Normalize the name
    name = path.stem
    name = name.replace("_", "-")
    assert all(c.isalnum() or c == "-" for c in name), path

    # See if this is a variant
    known_variants = [
        "fill",
    ]

    for variant in known_variants:
        if name.endswith(f"-{variant}"):
            name = name.removesuffix(f"-{variant}")
            break
    else:
        variant = None

    return name, variant


# == No changes should be required below this line ==


def main() -> None:
    # Find all files in the input directory
    print_chapter("Scanning files")

    if not INPUT_DIR.exists():
        fatal(f"The input directory [bold]{INPUT_DIR}[/bold] does not exist")

    in_files = []
    for path in INPUT_DIR.glob("**/*"):
        if path.is_file() and re.fullmatch(INPUT_NAME_PATTERN, path.name):
            in_files.append(path)

    print(f"Found {len(in_files)} file(s)")

    # Enforce an order so that the output is deterministic
    in_files.sort()

    # Apply the limit
    if LIMIT is not None:
        in_files = in_files[:LIMIT]
        print(f"Limiting to {LIMIT} file(s) (set `LIMIT` to `None` to disable)")

    # Process all files
    print_chapter("Processing files")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)

        with ProgressBar(max=len(in_files), unit="count") as bar:
            for ii, file_path in enumerate(in_files):
                bar.progress = ii

                # Extract the name and variant of the icon. If this function returns
                # `None` the file is skipped.
                parsed = name_from_icon_path(file_path.relative_to(INPUT_DIR))

                if parsed is None:
                    print(f"{file_path.name} -> [bold]skipped[/bold]")
                    continue

                icon_name, icon_variant = parsed
                variant_suffix = "" if icon_variant is None else f"/{icon_variant}"

                print(f"{file_path.name} -> {icon_name}{variant_suffix}")

                # Parse the SVG
                svg_str = file_path.read_text()
                tree = ET.fromstring(svg_str)

                # Strip the width / height if any
                if "width" in tree.attrib:
                    del tree.attrib["width"]

                if "height" in tree.attrib:
                    del tree.attrib["height"]

                # Determine the output path for this icon
                icon_out_path = tmp_dir

                if icon_variant is not None:
                    icon_out_path /= icon_variant

                icon_out_path /= f"{icon_name}.svg"

                # Suppress weird "ns0:" prefixes everywhere
                ET.register_namespace("", "http://www.w3.org/2000/svg")

                # Write the SVG
                icon_out_path.parent.mkdir(parents=True, exist_ok=True)

                with open(icon_out_path, "w") as f:
                    f.write(
                        ET.tostring(
                            tree,
                            encoding="unicode",
                            default_namespace=None,
                        )
                    )

        # Zip the temporary directory
        print_chapter("Zipping files")
        zip_path = OUTPUT_DIR / f"{SET_NAME}.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in tmp_dir.glob("**/*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(tmp_dir)
                    zipf.write(file_path, arcname=arcname)

    print_chapter(None)
    print(
        f"[bold]Done![/bold] You can find the result at [bold]{OUTPUT_DIR.resolve()}/{SET_NAME}.zip[/bold]"
    )


if __name__ == "__main__":
    main()
