"""Sampling utilities for reducing log entry volume."""

from typing import List, Dict, Any, Optional
import hashlib


def sample_by_rate(entries: List[Dict[str, Any]], rate: float) -> List[Dict[str, Any]]:
    """Return a uniform sample of entries by keeping every 1/rate-th entry.

    Args:
        entries: List of parsed log entry dicts.
        rate: Fraction to keep, between 0.0 (exclusive) and 1.0 (inclusive).

    Returns:
        Sampled subset of entries.

    Raises:
        ValueError: If rate is not in (0.0, 1.0].
    """
    if not (0.0 < rate <= 1.0):
        raise ValueError(f"rate must be in (0.0, 1.0], got {rate}")
    if rate == 1.0:
        return list(entries)
    step = int(round(1.0 / rate))
    return [entry for i, entry in enumerate(entries) if i % step == 0]


def sample_by_count(entries: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
    """Return at most `count` evenly-spaced entries.

    Args:
        entries: List of parsed log entry dicts.
        count: Maximum number of entries to return.

    Returns:
        Sampled subset of up to `count` entries.

    Raises:
        ValueError: If count is less than 1.
    """
    if count < 1:
        raise ValueError(f"count must be >= 1, got {count}")
    total = len(entries)
    if total <= count:
        return list(entries)
    step = total / count
    indices = {int(i * step) for i in range(count)}
    return [entry for i, entry in enumerate(entries) if i in indices]


def sample_by_field_hash(
    entries: List[Dict[str, Any]],
    field: str,
    rate: float,
) -> List[Dict[str, Any]]:
    """Deterministically sample entries based on a hash of a field value.

    Useful for keeping all log lines belonging to the same request/trace
    together while reducing overall volume.

    Args:
        entries: List of parsed log entry dicts.
        field: Field name to hash (e.g. 'request_id').
        rate: Fraction of distinct field values to retain (0.0, 1.0].

    Returns:
        Entries whose field hash falls within the kept bucket.
    """
    if not (0.0 < rate <= 1.0):
        raise ValueError(f"rate must be in (0.0, 1.0], got {rate}")
    threshold = int(rate * 2**16)
    result = []
    for entry in entries:
        value = str(entry.get(field, ""))
        digest = int(hashlib.md5(value.encode()).hexdigest()[:4], 16)
        if digest < threshold:
            result.append(entry)
    return result
