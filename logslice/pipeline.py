"""High-level pipeline: parse lines, apply filters, collect entries."""
from typing import Iterator, List, Dict, Any, Optional, IO

from logslice.parser import parse_line
from logslice.filters import apply_filters


def run_pipeline(
    lines: Iterator[str],
    *,
    min_level: Optional[str] = None,
    start: Optional[Any] = None,
    end: Optional[Any] = None,
    field_patterns: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Parse *lines* and return entries that pass all active filters.

    Parameters
    ----------
    lines:
        Iterable of raw log lines (strings).
    min_level:
        Minimum severity level string, e.g. ``"warning"``.
    start / end:
        Datetime bounds for time-range filtering.
    field_patterns:
        Mapping of field name -> regex pattern for field filtering.

    Returns
    -------
    List of parsed-and-filtered entry dicts.
    """
    field_patterns = field_patterns or {}
    results: List[Dict[str, Any]] = []

    for raw in lines:
        entry = parse_line(raw)
        if entry is None:
            continue

        if not apply_filters(
            entry,
            min_level=min_level,
            start=start,
            end=end,
            field_patterns=field_patterns,
        ):
            continue

        results.append(entry)

    return results


def run_pipeline_from_file(
    fh: IO[str],
    **kwargs: Any,
) -> List[Dict[str, Any]]:
    """Convenience wrapper that accepts an open file handle."""
    return run_pipeline(fh, **kwargs)
