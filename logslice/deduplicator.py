"""Deduplication utilities for log entries."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable, Iterator


def _entry_fingerprint(entry: dict, fields: list[str] | None = None) -> str:
    """Compute a stable fingerprint for a log entry.

    If *fields* is given, only those keys contribute to the fingerprint;
    otherwise every key/value pair is included (excluding the raw ``_raw``
    meta-key injected by the parser).
    """
    if fields:
        subset = {k: entry.get(k) for k in sorted(fields)}
    else:
        subset = {k: v for k, v in entry.items() if k != "_raw"}
        subset = dict(sorted(subset.items()))

    serialised = json.dumps(subset, sort_keys=True, default=str)
    return hashlib.sha256(serialised.encode()).hexdigest()


def deduplicate(
    entries: Iterable[dict],
    fields: list[str] | None = None,
    keep: str = "first",
) -> Iterator[dict]:
    """Yield unique log entries, dropping duplicates.

    Parameters
    ----------
    entries:
        Iterable of parsed log-entry dicts.
    fields:
        Optional list of field names to use for equality comparison.  When
        ``None`` all fields (except ``_raw``) are compared.
    keep:
        ``'first'`` (default) keeps the first occurrence; ``'last'`` keeps
        the last occurrence of each duplicate group.
    """
    if keep not in {"first", "last"}:
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")

    if keep == "first":
        seen: set[str] = set()
        for entry in entries:
            fp = _entry_fingerprint(entry, fields)
            if fp not in seen:
                seen.add(fp)
                yield entry
    else:
        # keep == "last": buffer everything, emit last winner per fingerprint
        ordered: list[str] = []
        mapping: dict[str, dict] = {}
        for entry in entries:
            fp = _entry_fingerprint(entry, fields)
            if fp not in mapping:
                ordered.append(fp)
            mapping[fp] = entry
        for fp in ordered:
            yield mapping[fp]


def count_duplicates(entries: Iterable[dict], fields: list[str] | None = None) -> int:
    """Return the number of duplicate entries (total entries minus unique entries)."""
    fingerprints: list[str] = [_entry_fingerprint(e, fields) for e in entries]
    return len(fingerprints) - len(set(fingerprints))
