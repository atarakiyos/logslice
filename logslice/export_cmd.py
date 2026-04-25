"""CLI sub-command helpers for the 'export' feature."""

from __future__ import annotations

import argparse
import sys
from typing import List, Sequence

from logslice.pipeline import run_pipeline_from_file
from logslice.writer import write_export


def build_export_parser(parent: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the 'export' sub-command on *parent* and return its parser."""
    p = parent.add_parser(
        "export",
        help="Export filtered log entries to CSV, TSV, or NDJSON.",
    )
    p.add_argument("input", help="Path to the input log file.")
    p.add_argument("-o", "--output", default=None, help="Destination file (stdout if omitted).")
    p.add_argument(
        "--format", "-f",
        choices=["csv", "tsv", "ndjson"],
        default=None,
        help="Output format. Inferred from --output extension when omitted.",
    )
    p.add_argument(
        "--fields",
        default=None,
        help="Comma-separated list of fields to include (column-based formats).",
    )
    p.add_argument("--level", default=None, help="Minimum log level filter.")
    p.add_argument("--from", dest="from_dt", default=None, help="Start timestamp (ISO 8601).")
    p.add_argument("--to", dest="to_dt", default=None, help="End timestamp (ISO 8601).")
    return p


def run_export_cmd(args: argparse.Namespace) -> int:
    """Execute the export sub-command. Returns an exit code."""
    from logslice.cli import _parse_dt  # local import to avoid circular deps

    from_dt = _parse_dt(args.from_dt) if args.from_dt else None
    to_dt = _parse_dt(args.to_dt) if args.to_dt else None
    fields: List[str] | None = (
        [f.strip() for f in args.fields.split(",")] if args.fields else None
    )

    try:
        entries = run_pipeline_from_file(
            args.input,
            min_level=args.level,
            from_dt=from_dt,
            to_dt=to_dt,
        )
    except FileNotFoundError:
        print(f"logslice export: file not found: {args.input}", file=sys.stderr)
        return 1

    write_export(entries, dest=args.output, fmt=args.format, fields=fields)
    return 0
