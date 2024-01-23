"""
Pretty-strings a traceback. The result looks very similar to Python's default,
but is colored and just tweaked in general.
"""


import html
import io
import linecache
import traceback
from pathlib import Path
from typing import *  # type: ignore

import revel
from revel import print


def _print_single_exception_raw(
    out: IO[str],
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
    relpath: Path | None = None,
) -> None:
    # Get the traceback as a list of frames
    tb_list = traceback.extract_tb(err.__traceback__)

    # Syntax errors are very special snowflakes and need separate treatment
    if isinstance(err, SyntaxError):
        tb_list.append(
            traceback.FrameSummary(
                filename=err.filename,  # type: ignore
                lineno=err.lineno,
                end_lineno=err.end_lineno,
                colno=err.offset,
                end_colno=err.end_offset,
                name="<module>",
                line=err.text,
                locals=None,
            )
        )

    # Lead-in
    out.write(f"{dim}Traceback (most recent call last):{nodim}\n")

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
        out.write(
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
            out.write(f"    {line}\n")

    # Actual error message
    out.write("\n")
    out.write(f"{bold}{red}{type(err).__name__}{nored}{nobold}")

    error_message = str(err)
    if error_message:
        out.write(f"{bold}: {escape(str(err))}{nobold}")


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
    relpath: Path | None = None,
) -> str:
    # Get a full list of exceptions to display
    exceptions = []

    while err is not None:
        exceptions.append(err)
        err = err.__context__ or err.__cause__  # type: ignore

    # Display them all
    out = io.StringIO()

    for ii, err in enumerate(reversed(exceptions)):
        _print_single_exception_raw(
            out,
            err,
            escape=escape,
            bold=bold,
            nobold=nobold,
            dim=dim,
            nodim=nodim,
            yellow=yellow,
            noyellow=noyellow,
            red=red,
            nored=nored,
            relpath=relpath,
        )

        if ii != len(exceptions) - 1:
            out.write("\n\n")
            out.write(
                f"The above exception was the direct cause of the following exception:\n\n"
            )

    return out.getvalue()


def format_exception_revel(
    err: BaseException,
    *,
    relpath: Path | None = None,
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
    relpath: Path | None = None,
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
