"""End-to-end report generation: pipeline + stats + formatted output."""
from typing import Any, Dict, IO, Iterator, List, Optional

from logslice.pipeline import run_pipeline
from logslice.stats import compute_stats, format_stats
from logslice.formatter import format_entry
from logslice.output import write_entries


def generate_report(
    lines: Iterator[str],
    output_fh: IO[str],
    *,
    min_level: Optional[str] = None,
    start: Optional[Any] = None,
    end: Optional[Any] = None,
    field_patterns: Optional[Dict[str, str]] = None,
    fmt: str = "json",
    show_stats: bool = False,
    stats_fh: Optional[IO[str]] = None,
) -> Dict[str, Any]:
    """Run the full logslice pipeline and write results.

    Parameters
    ----------
    lines:         Iterable of raw log lines.
    output_fh:     File-like object for filtered log output.
    min_level:     Minimum log level to include.
    start / end:   Datetime bounds.
    field_patterns: Field regex filters.
    fmt:           Output format — ``"json"``, ``"logfmt"``, or ``"pretty"``.
    show_stats:    If True, write a stats summary to *stats_fh*.
    stats_fh:      Destination for stats output (defaults to *output_fh*).

    Returns
    -------
    Stats dict produced by :func:`~logslice.stats.compute_stats`.
    """
    entries = run_pipeline(
        lines,
        min_level=min_level,
        start=start,
        end=end,
        field_patterns=field_patterns or {},
    )

    write_entries(entries, output_fh, fmt=fmt)

    stats = compute_stats(entries)

    if show_stats:
        dest = stats_fh if stats_fh is not None else output_fh
        dest.write("\n--- stats ---\n")
        dest.write(format_stats(stats))
        dest.write("\n")

    return stats
