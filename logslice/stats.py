"""Statistics and summary reporting for log entries."""
from collections import Counter
from typing import List, Dict, Any, Optional
from datetime import datetime


def compute_stats(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute summary statistics over a list of parsed log entries."""
    if not entries:
        return {
            "total": 0,
            "by_level": {},
            "earliest": None,
            "latest": None,
            "fields_seen": [],
        }

    level_counts: Counter = Counter()
    timestamps = []
    all_fields: set = set()

    for entry in entries:
        level = entry.get("level")
        if level:
            level_counts[level.upper()] += 1

        ts = entry.get("timestamp")
        if isinstance(ts, datetime):
            timestamps.append(ts)

        all_fields.update(entry.keys())

    earliest = min(timestamps).isoformat() if timestamps else None
    latest = max(timestamps).isoformat() if timestamps else None

    return {
        "total": len(entries),
        "by_level": dict(level_counts),
        "earliest": earliest,
        "latest": latest,
        "fields_seen": sorted(all_fields),
    }


def format_stats(stats: Dict[str, Any]) -> str:
    """Format statistics dict into a human-readable summary string."""
    lines = [
        f"Total entries : {stats['total']}",
        f"Earliest      : {stats['earliest'] or 'N/A'}",
        f"Latest        : {stats['latest'] or 'N/A'}",
    ]

    if stats["by_level"]:
        lines.append("By level      :")
        for level, count in sorted(stats["by_level"].items()):
            lines.append(f"  {level:<12} {count}")
    else:
        lines.append("By level      : N/A")

    if stats["fields_seen"]:
        lines.append("Fields seen   : " + ", ".join(stats["fields_seen"]))

    return "\n".join(lines)
