"""CLI entry point for logslice."""

import sys
from datetime import datetime
from typing import Optional

import click

from logslice.filters import apply_filters
from logslice.parser import parse_line


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise click.BadParameter(f"Cannot parse datetime: {value!r}")


@click.command()
@click.argument("logfile", type=click.Path(exists=True, readable=True), default="-")
@click.option("--level", "-l", default=None, help="Minimum log level (debug/info/warning/error/fatal).")
@click.option("--start", "-s", default=None, help="Start datetime (inclusive), e.g. 2024-01-01T00:00:00.")
@click.option("--end", "-e", default=None, help="End datetime (inclusive), e.g. 2024-01-01T23:59:59.")
@click.option(
    "--field", "-f", "field_patterns",
    multiple=True,
    type=(str, str),
    metavar="FIELD PATTERN",
    help="Filter by field regex, e.g. --field service auth.*",
)
@click.option("--count", "-c", is_flag=True, default=False, help="Print only the count of matching lines.")
def main(
    logfile: str,
    level: Optional[str],
    start: Optional[str],
    end: Optional[str],
    field_patterns: tuple,
    count: bool,
) -> None:
    """Filter structured log files by time range, level, or field patterns."""
    start_dt = _parse_dt(start)
    end_dt = _parse_dt(end)
    patterns = dict(field_patterns) if field_patterns else None

    source = click.open_file(logfile)
    matched = 0

    try:
        for line in source:
            entry = parse_line(line)
            if entry is None:
                continue
            if apply_filters(entry, level=level, start=start_dt, end=end_dt, field_patterns=patterns):
                matched += 1
                if not count:
                    click.echo(line, nl=False)
    finally:
        if source is not sys.stdin:
            source.close()

    if count:
        click.echo(matched)


if __name__ == "__main__":
    main()
