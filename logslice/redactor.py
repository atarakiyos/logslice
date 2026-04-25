"""Field redaction and masking utilities for sensitive log data."""

import re
from typing import Any, Dict, List, Optional, Pattern

# Default patterns for common sensitive fields
DEFAULT_SENSITIVE_KEYS = {"password", "passwd", "secret", "token", "api_key", "apikey", "auth"}
REDACT_PLACEHOLDER = "[REDACTED]"
MASK_CHAR = "*"


def redact_fields(entry: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Replace the values of the given field names with a redaction placeholder."""
    result = dict(entry)
    for field in fields:
        if field in result:
            result[field] = REDACT_PLACEHOLDER
    return result


def mask_field(entry: Dict[str, Any], field: str, visible_chars: int = 4) -> Dict[str, Any]:
    """Partially mask a field value, preserving the last `visible_chars` characters."""
    result = dict(entry)
    if field not in result:
        return result
    value = str(result[field])
    if len(value) <= visible_chars:
        result[field] = MASK_CHAR * len(value)
    else:
        result[field] = MASK_CHAR * (len(value) - visible_chars) + value[-visible_chars:]
    return result


def redact_pattern(entry: Dict[str, Any], pattern: str, replacement: str = REDACT_PLACEHOLDER) -> Dict[str, Any]:
    """Replace regex pattern matches within all string field values."""
    compiled: Pattern = re.compile(pattern)
    result = {}
    for key, value in entry.items():
        if isinstance(value, str):
            result[key] = compiled.sub(replacement, value)
        else:
            result[key] = value
    return result


def auto_redact(entry: Dict[str, Any], extra_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """Automatically redact fields whose names match known sensitive key names."""
    sensitive = DEFAULT_SENSITIVE_KEYS.copy()
    if extra_keys:
        sensitive.update(k.lower() for k in extra_keys)
    fields_to_redact = [k for k in entry if k.lower() in sensitive]
    return redact_fields(entry, fields_to_redact)


def apply_redaction(
    entries: List[Dict[str, Any]],
    redact: Optional[List[str]] = None,
    mask: Optional[str] = None,
    pattern: Optional[str] = None,
    auto: bool = False,
) -> List[Dict[str, Any]]:
    """Apply one or more redaction strategies to a list of entries."""
    result = []
    for entry in entries:
        e = dict(entry)
        if auto:
            e = auto_redact(e)
        if redact:
            e = redact_fields(e, redact)
        if mask:
            e = mask_field(e, mask)
        if pattern:
            e = redact_pattern(e, pattern)
        result.append(e)
    return result
