"""Export pipeline results to various file formats (CSV, NDJSON, TSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import Iterable, List

from logslice.parser import LogEntry


def _collect_fields(entries: List[LogEntry]) -> List[str]:
    """Return a stable ordered list of all field keys across entries."""
    seen: dict[str, None] = {}
    for entry in entries:
        for key in entry:
            if key != "raw":
                seen[key] = None
    return list(seen)


def export_csv(entries: List[LogEntry], fields: List[str] | None = None) -> str:
    """Serialise entries to CSV string. Uses all discovered fields if *fields* is None."""
    if not entries:
        return ""
    cols = fields if fields is not None else _collect_fields(entries)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for entry in entries:
        writer.writerow({col: entry.get(col, "") for col in cols})
    return buf.getvalue()


def export_ndjson(entries: Iterable[LogEntry]) -> str:
    """Serialise entries to newline-delimited JSON."""
    lines = []
    for entry in entries:
        payload = {k: v for k, v in entry.items() if k != "raw"}
        lines.append(json.dumps(payload, default=str))
    return "\n".join(lines) + ("\n" if lines else "")


def export_tsv(entries: List[LogEntry], fields: List[str] | None = None) -> str:
    """Serialise entries to tab-separated values string."""
    if not entries:
        return ""
    cols = fields if fields is not None else _collect_fields(entries)
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=cols, extrasaction="ignore",
        delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    for entry in entries:
        writer.writerow({col: entry.get(col, "") for col in cols})
    return buf.getvalue()


def export_entries(entries: List[LogEntry], fmt: str = "ndjson", fields: List[str] | None = None) -> str:
    """Dispatch to the appropriate exporter. *fmt* must be 'csv', 'tsv', or 'ndjson'."""
    fmt = fmt.lower()
    if fmt == "csv":
        return export_csv(entries, fields)
    if fmt == "tsv":
        return export_tsv(entries, fields)
    if fmt == "ndjson":
        return export_ndjson(entries)
    raise ValueError(f"Unsupported export format: {fmt!r}")
