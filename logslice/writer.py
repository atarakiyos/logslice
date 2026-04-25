"""Write exported content to a file path or stdout."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from logslice.exporter import export_entries
from logslice.parser import LogEntry

_EXTENSION_MAP: dict[str, str] = {
    ".csv": "csv",
    ".tsv": "tsv",
    ".ndjson": "ndjson",
    ".jsonl": "ndjson",
}


def _fmt_from_path(path: Path) -> str:
    """Infer export format from file extension, defaulting to 'ndjson'."""
    return _EXTENSION_MAP.get(path.suffix.lower(), "ndjson")


def write_export(
    entries: List[LogEntry],
    dest: str | None = None,
    fmt: str | None = None,
    fields: List[str] | None = None,
) -> None:
    """Export *entries* to *dest* (file path) or stdout if *dest* is None.

    Parameters
    ----------
    entries:
        Parsed log entries to export.
    dest:
        Destination file path. ``None`` writes to stdout.
    fmt:
        Explicit format override ('csv', 'tsv', 'ndjson'). When *None* the
        format is inferred from the *dest* extension.
    fields:
        Ordered list of field names for column-based formats.
    """
    resolved_fmt = fmt
    if resolved_fmt is None:
        if dest is not None:
            resolved_fmt = _fmt_from_path(Path(dest))
        else:
            resolved_fmt = "ndjson"

    content = export_entries(entries, fmt=resolved_fmt, fields=fields)

    if dest is None:
        sys.stdout.write(content)
    else:
        Path(dest).write_text(content, encoding="utf-8")
