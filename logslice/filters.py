"""Filter functions for log entries."""

import re
from datetime import datetime
from typing import Any, Optional

from logslice.parser import parse_timestamp


def filter_by_level(
    entry: dict[str, Any], level: str
) -> bool:
    """Return True if entry level is >= the given minimum level."""
    order = ["debug", "info", "warning", "error", "fatal", "critical"]
    entry_level = str(entry.get("level", "")).lower()
    min_level = level.lower()
    if entry_level not in order or min_level not in order:
        return True  # don't filter if levels are unknown
    return order.index(entry_level) >= order.index(min_level)


def filter_by_time_range(
    entry: dict[str, Any],
    start: Optional[datetime],
    end: Optional[datetime],
) -> bool:
    """Return True if entry timestamp falls within [start, end]."""
    if start is None and end is None:
        return True

    raw_ts = entry.get("timestamp")
    if raw_ts is None:
        return False

    ts = parse_timestamp(str(raw_ts))
    if ts is None:
        return False

    # Make both naive for comparison if needed
    if ts.tzinfo is not None:
        ts = ts.replace(tzinfo=None)

    if start is not None and ts < start:
        return False
    if end is not None and ts > end:
        return False
    return True


def filter_by_field_pattern(
    entry: dict[str, Any], field: str, pattern: str
) -> bool:
    """Return True if entry[field] matches the given regex pattern."""
    value = entry.get(field)
    if value is None:
        return False
    try:
        return bool(re.search(pattern, str(value)))
    except re.error:
        return False


def apply_filters(
    entry: dict[str, Any],
    level: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    field_patterns: Optional[dict[str, str]] = None,
) -> bool:
    """Apply all active filters to a log entry. Returns True if it passes."""
    if level and not filter_by_level(entry, level):
        return False
    if (start or end) and not filter_by_time_range(entry, start, end):
        return False
    if field_patterns:
        for field, pattern in field_patterns.items():
            if not filter_by_field_pattern(entry, field, pattern):
                return False
    return True
