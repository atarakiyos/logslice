"""Output writer for logslice — streams formatted entries to a file or stdout."""

import sys
from typing import Iterable, Dict, Any, Optional, TextIO

from logslice.formatter import format_entry, SUPPORTED_FORMATS


def write_entries(
    entries: Iterable[Dict[str, Any]],
    fmt: str = "json",
    dest: Optional[TextIO] = None,
    count_limit: Optional[int] = None,
) -> int:
    """Write formatted log entries to *dest* (defaults to stdout).

    Args:
        entries: Iterable of parsed log entry dicts.
        fmt: Output format — one of SUPPORTED_FORMATS.
        dest: File-like object to write to; defaults to sys.stdout.
        count_limit: If set, stop after emitting this many entries.

    Returns:
        Number of entries written.

    Raises:
        ValueError: If *fmt* is not a supported format.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format {fmt!r}. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    out = dest if dest is not None else sys.stdout
    written = 0

    for entry in entries:
        if count_limit is not None and written >= count_limit:
            break
        line = format_entry(entry, fmt=fmt)
        if line is not None:
            out.write(line + "\n")
            written += 1

    return written
