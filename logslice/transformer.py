"""Field transformation utilities for log entries."""

from typing import Any, Callable, Dict, List, Optional


Entry = Dict[str, Any]
TransformFn = Callable[[Any], Any]


def rename_field(entries: List[Entry], old_name: str, new_name: str) -> List[Entry]:
    """Rename a field in every entry that contains it."""
    result = []
    for entry in entries:
        if old_name in entry:
            updated = {k: v for k, v in entry.items() if k != old_name}
            updated[new_name] = entry[old_name]
            result.append(updated)
        else:
            result.append(entry)
    return result


def drop_fields(entries: List[Entry], fields: List[str]) -> List[Entry]:
    """Remove specified fields from every entry."""
    drop_set = set(fields)
    return [
        {k: v for k, v in entry.items() if k not in drop_set}
        for entry in entries
    ]


def keep_fields(entries: List[Entry], fields: List[str]) -> List[Entry]:
    """Keep only the specified fields in every entry (plus 'raw')."""
    keep_set = set(fields) | {"raw"}
    return [
        {k: v for k, v in entry.items() if k in keep_set}
        for entry in entries
    ]


def apply_transform(entries: List[Entry], field: str, fn: TransformFn) -> List[Entry]:
    """Apply a transformation function to a specific field in every entry."""
    result = []
    for entry in entries:
        if field in entry:
            updated = dict(entry)
            try:
                updated[field] = fn(entry[field])
            except Exception:
                pass  # leave original value on error
            result.append(updated)
        else:
            result.append(entry)
    return result


def add_field(entries: List[Entry], field: str, value: Any) -> List[Entry]:
    """Add a constant field to every entry (does not overwrite existing)."""
    result = []
    for entry in entries:
        if field not in entry:
            updated = dict(entry)
            updated[field] = value
            result.append(updated)
        else:
            result.append(entry)
    return result


def coerce_field_to_int(entries: List[Entry], field: str) -> List[Entry]:
    """Attempt to coerce a field's value to int in every entry."""
    def _to_int(v: Any) -> int:
        return int(v)
    return apply_transform(entries, field, _to_int)


def coerce_field_to_float(entries: List[Entry], field: str) -> List[Entry]:
    """Attempt to coerce a field's value to float in every entry."""
    def _to_float(v: Any) -> float:
        return float(v)
    return apply_transform(entries, field, _to_float)
