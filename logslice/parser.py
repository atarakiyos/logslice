"""Structured log line parser supporting JSON and logfmt formats."""

import json
from datetime import datetime
from typing import Any, Optional


LOG_LEVELS = {"debug", "info", "warn", "warning", "error", "fatal", "critical"}


def parse_line(line: str) -> Optional[dict[str, Any]]:
    """Parse a single log line into a dictionary.

    Tries JSON first, then logfmt. Returns None if parsing fails.
    """
    line = line.strip()
    if not line:
        return None

    if line.startswith("{"):
        return _parse_json(line)
    return _parse_logfmt(line)


def _parse_json(line: str) -> Optional[dict[str, Any]]:
    try:
        entry = json.loads(line)
        if isinstance(entry, dict):
            _normalize_fields(entry)
            return entry
    except json.JSONDecodeError:
        pass
    return None


def _parse_logfmt(line: str) -> Optional[dict[str, Any]]:
    """Parse a logfmt-style line: key=value key="quoted value" ..."""
    entry: dict[str, Any] = {}
    i = 0
    while i < len(line):
        # skip whitespace
        while i < len(line) and line[i] == " ":
            i += 1
        if i >= len(line):
            break
        eq = line.find("=", i)
        if eq == -1:
            break
        key = line[i:eq]
        i = eq + 1
        if i < len(line) and line[i] == '"':
            end = line.find('"', i + 1)
            if end == -1:
                end = len(line)
            value = line[i + 1:end]
            i = end + 1
        else:
            space = line.find(" ", i)
            if space == -1:
                space = len(line)
            value = line[i:space]
            i = space
        entry[key] = value

    if not entry:
        return None
    _normalize_fields(entry)
    return entry


def _normalize_fields(entry: dict[str, Any]) -> None:
    """Normalize common timestamp and level field names in-place."""
    for ts_key in ("timestamp", "time", "ts", "@timestamp"):
        if ts_key in entry and "timestamp" not in entry:
            entry["timestamp"] = entry[ts_key]
            break

    for lvl_key in ("level", "lvl", "severity", "loglevel"):
        if lvl_key in entry:
            raw = str(entry[lvl_key]).lower()
            entry["level"] = "warning" if raw == "warn" else raw
            break


def parse_timestamp(value: str) -> Optional[datetime]:
    """Attempt to parse a timestamp string into a datetime object."""
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None
