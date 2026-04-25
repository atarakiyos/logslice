"""CLI sub-command for redacting sensitive fields from log streams."""

import argparse
import sys
from typing import List, Optional

from logslice.parser import parse_line
from logslice.redactor import apply_redaction
from logslice.formatter import format_entry


def build_redact_parser(subparsers=None) -> argparse.ArgumentParser:
    """Create and return the argument parser for the 'redact' sub-command."""
    kwargs = dict(
        description="Redact or mask sensitive fields in structured log entries."
    )
    if subparsers is not None:
        parser = subparsers.add_parser("redact", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="logslice redact", **kwargs)

    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Input log file (default: stdin).",
    )
    parser.add_argument(
        "--redact",
        metavar="FIELD",
        nargs="+",
        default=[],
        help="Field names to fully redact.",
    )
    parser.add_argument(
        "--mask",
        metavar="FIELD",
        default=None,
        help="Field name to partially mask (keeps last 4 chars).",
    )
    parser.add_argument(
        "--pattern",
        metavar="REGEX",
        default=None,
        help="Regex pattern to redact from all string field values.",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically redact common sensitive field names.",
    )
    parser.add_argument(
        "--fmt",
        choices=["json", "logfmt", "pretty"],
        default="json",
        help="Output format (default: json).",
    )
    return parser


def run_redact_cmd(args: argparse.Namespace, lines: Optional[List[str]] = None) -> None:
    """Execute the redact command given parsed arguments."""
    if lines is None:
        if args.input == "-":
            lines = sys.stdin
        else:
            with open(args.input) as fh:
                lines = fh.readlines()

    entries = []
    for line in lines:
        entry = parse_line(line)
        if entry is not None:
            entries.append(entry)

    redacted = apply_redaction(
        entries,
        redact=args.redact or None,
        mask=args.mask,
        pattern=args.pattern,
        auto=args.auto,
    )

    for entry in redacted:
        print(format_entry(entry, fmt=args.fmt))
