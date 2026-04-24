"""Output formatters for logslice — controls how filtered log entries are rendered."""

import json
from typing import Any, Dict, Optional


SUPPORTED_FORMATS = ("json", "logfmt", "pretty")


def format_json(entry: Dict[str, Any]) -> str:
    """Serialize a log entry back to a compact JSON string."""
    return json.dumps(entry, default=str)


def format_logfmt(entry: Dict[str, Any]) -> str:
    """Serialize a log entry as a logfmt key=value string."""
    parts = []
    for key, value in entry.items():
        value_str = str(value) if not isinstance(value, str) else value
        # Quote values that contain spaces or special characters
        if any(c in value_str for c in (" ", "=", '"')):
            value_str = '"' + value_str.replace('"', '\\"') + '"'
        parts.append(f"{key}={value_str}")
    return " ".join(parts)


def format_pretty(entry: Dict[str, Any]) -> str:
    """Render a log entry as a human-readable single line."""
    timestamp = entry.get("timestamp", entry.get("ts", ""))
    level = entry.get("level", "").upper()
    message = entry.get("message", entry.get("msg", ""))

    extras = {
        k: v
        for k, v in entry.items()
        if k not in ("timestamp", "ts", "level", "message", "msg")
    }

    base = f"[{timestamp}] {level:<8} {message}"
    if extras:
        extra_str = "  " + "  ".join(f"{k}={v}" for k, v in extras.items())
        return base + extra_str
    return base


def format_entry(
    entry: Dict[str, Any], fmt: str = "json"
) -> Optional[str]:
    """Format a single log entry using the specified output format.

    Args:
        entry: Parsed log entry dictionary.
        fmt: One of 'json', 'logfmt', or 'pretty'.

    Returns:
        Formatted string, or None if the format is unsupported.

    Raises:
        ValueError: If fmt is not one of the supported formats.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format {fmt!r}. Must be one of: {', '.join(SUPPORTED_FORMATS)}"
        )
    if fmt == "json":
        return format_json(entry)
    if fmt == "logfmt":
        return format_logfmt(entry)
    if fmt == "pretty":
        return format_pretty(entry)
    return None
