"""High-level pipeline for parsing, filtering, sampling, and formatting logs."""

from typing import List, Dict, Any, Optional, TextIO

from logslice.parser import parse_line
from logslice.filters import apply_filters
from logslice.sampler import sample_by_rate, sample_by_count
from logslice.formatter import format_entry


def run_pipeline(
    lines: List[str],
    *,
    min_level: Optional[str] = None,
    start: Optional[Any] = None,
    end: Optional[Any] = None,
    field_patterns: Optional[Dict[str, str]] = None,
    sample_rate: Optional[float] = None,
    sample_count: Optional[int] = None,
    output_format: str = "json",
) -> List[str]:
    """Parse, filter, optionally sample, and format log lines.

    Sampling is applied after filtering.  If both *sample_rate* and
    *sample_count* are provided, *sample_rate* takes precedence.

    Args:
        lines: Raw text lines from a log source.
        min_level: Minimum severity level string (e.g. ``"warning"``).
        start: Earliest timestamp (datetime) to include.
        end: Latest timestamp (datetime) to include.
        field_patterns: Mapping of field name -> regex pattern to match.
        sample_rate: Fraction of filtered entries to retain (0.0, 1.0].
        sample_count: Maximum number of entries to retain after filtering.
        output_format: One of ``"json"``, ``"logfmt"``, or ``"pretty"``.

    Returns:
        List of formatted output strings, one per retained entry.
    """
    entries: List[Dict[str, Any]] = []
    for line in lines:
        entry = parse_line(line)
        if entry is not None:
            entries.append(entry)

    entries = apply_filters(
        entries,
        min_level=min_level,
        start=start,
        end=end,
        field_patterns=field_patterns or {},
    )

    if sample_rate is not None:
        entries = sample_by_rate(entries, sample_rate)
    elif sample_count is not None:
        entries = sample_by_count(entries, sample_count)

    return [format_entry(e, fmt=output_format) for e in entries]


def run_pipeline_from_file(
    fh: TextIO,
    **kwargs: Any,
) -> List[str]:
    """Convenience wrapper that reads lines from an open file handle.

    Args:
        fh: Readable text file-like object.
        **kwargs: Forwarded verbatim to :func:`run_pipeline`.

    Returns:
        List of formatted output strings.
    """
    lines = [line.rstrip("\n") for line in fh]
    return run_pipeline(lines, **kwargs)
