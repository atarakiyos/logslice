"""merger.py — Merge and interleave multiple streams of log entries.

Provides utilities to combine log entries from several sources into a
single chronologically sorted stream, with optional de-duplication and
source tagging.
"""

from __future__ import annotations

import heapq
from typing import Iterable, Iterator, List, Optional, Sequence

# Sentinel used when an entry has no parseable timestamp.
_NO_TS = ""


def _sort_key(entry: dict) -> tuple:
    """Return a stable sort key for an entry.

    Entries with a timestamp sort before those without.  Within the same
    timestamp string, the source tag (if present) is used as a tiebreaker
    so that the merge is deterministic.
    """
    ts = entry.get("timestamp") or _NO_TS
    src = entry.get("_source") or ""
    return (ts, src)


def tag_entries(entries: Iterable[dict], source: str) -> List[dict]:
    """Return copies of *entries* with a ``_source`` field set to *source*.

    The original dicts are **not** mutated.

    Args:
        entries: Iterable of parsed log-entry dicts.
        source:  A label identifying where these entries came from
                 (e.g. a filename or service name).

    Returns:
        A list of new dicts, each containing all original fields plus
        ``_source``.
    """
    tagged: List[dict] = []
    for entry in entries:
        tagged_entry = dict(entry)
        tagged_entry["_source"] = source
        tagged.append(tagged_entry)
    return tagged


def merge_sorted(
    streams: Sequence[Iterable[dict]],
    key=_sort_key,
) -> Iterator[dict]:
    """Merge *streams* into a single iterator sorted by *key*.

    Each stream is assumed to be **already sorted** by *key*.  A heap-based
    k-way merge is used so that the operation is O(N log k) where N is the
    total number of entries and k is the number of streams.

    Args:
        streams: Sequence of iterables, each yielding sorted log-entry dicts.
        key:     Callable that returns a comparable sort key for an entry.
                 Defaults to ``_sort_key`` (timestamp then source tag).

    Yields:
        Log-entry dicts in merged sorted order.
    """
    # heapq requires comparable items; wrap each entry with its key and an
    # integer stream index to break ties without comparing raw dicts.
    iterators = [iter(s) for s in streams]
    heap: list = []

    for stream_idx, it in enumerate(iterators):
        try:
            entry = next(it)
            heapq.heappush(heap, (key(entry), stream_idx, entry, it))
        except StopIteration:
            pass

    while heap:
        sort_k, stream_idx, entry, it = heapq.heappop(heap)
        yield entry
        try:
            next_entry = next(it)
            heapq.heappush(heap, (key(next_entry), stream_idx, next_entry, it))
        except StopIteration:
            pass


def merge_unsorted(
    streams: Sequence[Iterable[dict]],
    key=_sort_key,
) -> List[dict]:
    """Collect all entries from *streams* and return them sorted by *key*.

    Unlike :func:`merge_sorted`, this function does **not** require the
    individual streams to be pre-sorted.  All entries are buffered in memory
    before sorting, which is suitable for moderate-sized inputs.

    Args:
        streams: Sequence of iterables yielding log-entry dicts.
        key:     Sort-key callable (same default as :func:`merge_sorted`).

    Returns:
        A new list containing every entry from all streams, sorted by *key*.
    """
    combined: List[dict] = []
    for stream in streams:
        combined.extend(stream)
    combined.sort(key=key)
    return combined


def merge_entries(
    streams: Sequence[Iterable[dict]],
    sources: Optional[Sequence[str]] = None,
    pre_sorted: bool = False,
) -> List[dict]:
    """High-level merge helper used by the CLI and pipeline.

    Optionally tags each stream with a source label, then merges all
    streams into a single sorted list.

    Args:
        streams:     One or more iterables of log-entry dicts.
        sources:     Optional sequence of source labels, one per stream.
                     When provided, each entry receives a ``_source`` field.
        pre_sorted:  If ``True``, assume each stream is already sorted and
                     use the efficient k-way heap merge.  Otherwise, collect
                     all entries and sort them in one pass.

    Returns:
        A list of merged, sorted log-entry dicts.
    """
    prepared: List[Iterable[dict]] = []
    for i, stream in enumerate(streams):
        if sources and i < len(sources):
            prepared.append(tag_entries(stream, sources[i]))
        else:
            prepared.append(stream)

    if pre_sorted:
        return list(merge_sorted(prepared))
    return merge_unsorted(prepared)
