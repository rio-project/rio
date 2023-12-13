"""
Pretty-strings a traceback. The result looks very similar to Python's default,
but is colored and just tweaked in general.
"""


import html
import linecache
import traceback
from pathlib import Path
from typing import *  # type: ignore

import revel
from revel import print


def format_exception_raw(
    err: BaseException,
    *,
    escape: Callable[[str], str],
    bold: str,
    nobold: str,
    dim: str,
    nodim: str,
    yellow: str,
    noyellow: str,
    red: str,
    nored: str,
    relpath: Optional[Path] = None,
) -> str:
    # Get the traceback as a list of frames
    tb_list = traceback.extract_tb(err.__traceback__)

    # Lead-in
    chunks = []
    chunks.append(f"{dim}Traceback (most recent call last):{nodim}\n")

    # Iterate through frames
    for frame in tb_list:
        # Drop any leading frames which are part of Rio
        # TODO

        # Make paths relative to the relpath if they're inside it
        frame_path = Path(frame.filename)

        if relpath is not None and frame_path.is_absolute():
            try:
                frame_path = frame_path.relative_to(relpath)
            except ValueError:
                pass

        # Format the file location
        chunks.append(
            f"  {dim}File{nodim} {yellow}{escape(str(frame_path))}{noyellow}{dim}, {nodim}{yellow}line {frame.lineno}{noyellow}{dim}, in {escape(frame.name)}{nodim}\n"
        )

        # Display the source code from that line
        #
        # Insanely, the line in the frame has been stripped. Fetch it again.
        assert frame.lineno is not None  # Doesn't seem to happen, ever
        line = linecache.getline(frame.filename, frame.lineno)

        if line.strip():
            # If this is the last line, highlight the error
            if (
                frame is tb_list[-1]
                and hasattr(frame, "colno")
                and hasattr(frame, "end_colno")
            ):
                assert frame.colno is not None
                assert frame.end_colno is not None

                before = escape(line[: frame.colno])
                error = escape(line[frame.colno : frame.end_colno])
                after = escape(line[frame.end_colno :])
                line = f"{before}{red}{error}{nored}{after}"
            else:
                line = escape(line)

            # NOW strip it
            line = line.strip()
            chunks.append(f"    {line}\n")

    # Actual error message
    chunks.append("\n")
    chunks.append(
        f"{bold}{red}{type(err).__name__}{nored}: {escape(str(err))}{nobold}{nobold}"
    )

    # Combine the formatted frames into a string
    return "".join(chunks)


def format_exception_revel(
    err: BaseException,
    *,
    relpath: Optional[Path] = None,
) -> str:
    return format_exception_raw(
        err,
        bold="[bold]",
        nobold="[/]",
        dim="[dim]",
        nodim="[/]",
        yellow="[yellow]",
        noyellow="[/]",
        red="[red]",
        nored="[/]",
        escape=revel.escape,
        relpath=relpath,
    )


def format_exception_html(
    err: BaseException,
    *,
    relpath: Optional[Path] = None,
) -> str:
    result = format_exception_raw(
        err,
        bold='<span class="rio-traceback-bold">',
        nobold="</span>",
        dim='<span class="rio-traceback-dim">',
        nodim="</span>",
        yellow='<span class="rio-traceback-yellow">',
        noyellow="</span>",
        red='<span class="rio-traceback-red">',
        nored="</span>",
        escape=html.escape,
        relpath=relpath,
    )

    return result.replace("\n", "<br>")
