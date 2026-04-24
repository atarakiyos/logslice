"""Aggregation utilities for grouped log analysis."""

from collections import defaultdict
from typing import Any, Dict, List, Optional


def group_by_field(
    entries: List[Dict[str, Any]],
    field: str,
) -> Dict[str, List[Dict[str, Any]]]:
    """Group log entries by the value of a given field."""
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        key = str(entry.get(field, "__missing__"))
        groups[key].append(entry)
    return dict(groups)


def count_by_field(
    entries: List[Dict[str, Any]],
    field: str,
) -> Dict[str, int]:
    """Return a mapping of field value -> occurrence count."""
    counts: Dict[str, int] = defaultdict(int)
    for entry in entries:
        key = str(entry.get(field, "__missing__"))
        counts[key] += 1
    return dict(counts)


def top_values(
    counts: Dict[str, int],
    n: int = 10,
) -> List[tuple]:
    """Return the top-n (value, count) pairs sorted by count descending."""
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]


def aggregate_numeric_field(
    entries: List[Dict[str, Any]],
    field: str,
) -> Optional[Dict[str, float]]:
    """Compute min, max, mean for a numeric field across entries.

    Returns None if no numeric values are found.
    """
    values: List[float] = []
    for entry in entries:
        raw = entry.get(field)
        if raw is None:
            continue
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            continue

    if not values:
        return None

    return {
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
        "count": float(len(values)),
    }
