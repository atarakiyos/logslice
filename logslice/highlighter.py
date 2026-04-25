"""Terminal colour highlighting for log output."""

from __future__ import annotations

import re
from typing import Dict, Optional

# ANSI escape codes
_RESET = "\033[0m"
_COLOURS: Dict[str, str] = {
    "red": "\033[31m",
    "yellow": "\033[33m",
    "green": "\033[32m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
    "bold": "\033[1m",
    "dim": "\033[2m",
}

_LEVEL_COLOURS: Dict[str, str] = {
    "ERROR": _COLOURS["red"],
    "CRITICAL": _COLOURS["red"] + _COLOURS["bold"],
    "WARNING": _COLOURS["yellow"],
    "INFO": _COLOURS["green"],
    "DEBUG": _COLOURS["dim"],
}


def _wrap(text: str, colour: str) -> str:
    """Wrap *text* with an ANSI colour code and reset."""
    return f"{colour}{text}{_RESET}"


def highlight_level(level: Optional[str]) -> str:
    """Return a colourised version of *level*, or the original string."""
    if level is None:
        return ""
    normalised = level.upper()
    colour = _LEVEL_COLOURS.get(normalised)
    if colour:
        return _wrap(normalised, colour)
    return level


def highlight_pattern(text: str, pattern: str, colour: str = "cyan") -> str:
    """Highlight every occurrence of *pattern* (regex) inside *text*."""
    colour_code = _COLOURS.get(colour, _COLOURS["cyan"])
    try:
        return re.sub(
            pattern,
            lambda m: _wrap(m.group(0), colour_code),
            text,
        )
    except re.error:
        return text


def highlight_entry(entry: dict, pattern: Optional[str] = None) -> str:
    """Produce a human-readable, colourised one-liner for *entry*.

    If *pattern* is supplied every matching substring in the message is
    highlighted in cyan.
    """
    ts = _wrap(entry.get("timestamp", ""), _COLOURS["dim"])
    level_raw = entry.get("level", "")
    level_str = highlight_level(level_raw)
    msg = entry.get("message", entry.get("msg", ""))
    if pattern and msg:
        msg = highlight_pattern(str(msg), pattern)
    parts = [p for p in (ts, level_str, msg) if p]
    return " ".join(parts)
