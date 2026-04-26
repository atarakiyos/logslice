"""Split a stream of log entries into chunks by time window or count."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Generator, List, Optional


def split_by_count(entries: List[Dict], chunk_size: int) -> Generator[List[Dict], None, None]:
    """Yield successive chunks of *chunk_size* entries."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    for i in range(0, len(entries), chunk_size):
        yield entries[i : i + chunk_size]


def split_by_time_window(
    entries: List[Dict],
    window_seconds: float,
    timestamp_field: str = "timestamp",
) -> Generator[List[Dict], None, None]:
    """Yield groups of entries that fall within *window_seconds* of each other.

    Entries that lack a parseable timestamp are placed in the current window.
    """
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")

    window = timedelta(seconds=window_seconds)
    current_bucket: List[Dict] = []
    bucket_start: Optional[datetime] = None

    for entry in entries:
        ts = entry.get(timestamp_field)
        if isinstance(ts, datetime):
            if bucket_start is None:
                bucket_start = ts
            if ts - bucket_start >= window:
                if current_bucket:
                    yield current_bucket
                current_bucket = [entry]
                bucket_start = ts
                continue
        current_bucket.append(entry)

    if current_bucket:
        yield current_bucket


def split_by_field(
    entries: List[Dict],
    field: str,
    sentinel: str = "__missing__",
) -> Dict[str, List[Dict]]:
    """Partition entries into a dict keyed by the value of *field*."""
    result: Dict[str, List[Dict]] = {}
    for entry in entries:
        key = str(entry.get(field, sentinel))
        result.setdefault(key, []).append(entry)
    return result
