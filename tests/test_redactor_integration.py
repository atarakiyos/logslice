"""Integration tests combining redactor with parser and formatter."""

import json
from logslice.parser import parse_line
from logslice.redactor import apply_redaction
from logslice.formatter import format_entry
from logslice.redactor import REDACT_PLACEHOLDER


def _roundtrip(raw_lines, **redact_kwargs):
    """Parse lines -> redact -> format back to JSON dicts."""
    entries = [parse_line(l) for l in raw_lines]
    entries = [e for e in entries if e is not None]
    redacted = apply_redaction(entries, **redact_kwargs)
    return [json.loads(format_entry(e, fmt="json")) for e in redacted]


def test_roundtrip_redact_preserves_structure():
    lines = [json.dumps({"level": "INFO", "msg": "ok", "token": "abc"}) + "\n"]
    result = _roundtrip(lines, redact=["token"])
    assert result[0]["level"] == "INFO"
    assert result[0]["msg"] == "ok"
    assert result[0]["token"] == REDACT_PLACEHOLDER


def test_roundtrip_auto_redact_multiple_entries():
    lines = [
        json.dumps({"level": "INFO", "msg": "login", "password": "p1"}) + "\n",
        json.dumps({"level": "WARN", "msg": "retry", "password": "p2"}) + "\n",
    ]
    result = _roundtrip(lines, auto=True)
    assert all(e["password"] == REDACT_PLACEHOLDER for e in result)


def test_roundtrip_mask_partial():
    lines = [json.dumps({"level": "DEBUG", "msg": "x", "api_key": "ABCDEF9876"}) + "\n"]
    result = _roundtrip(lines, mask="api_key")
    assert result[0]["api_key"].endswith("9876")


def test_roundtrip_pattern_on_message():
    lines = [json.dumps({"level": "ERROR", "msg": "failed for user@corp.io"}) + "\n"]
    result = _roundtrip(lines, pattern=r"[\w.+-]+@[\w-]+\.[\w.]+")
    assert "user@corp.io" not in result[0]["msg"]
    assert REDACT_PLACEHOLDER in result[0]["msg"]


def test_roundtrip_combined_strategies():
    lines = [
        json.dumps({"level": "INFO", "msg": "hi user@x.com", "secret": "s", "token": "tok123"}) + "\n"
    ]
    result = _roundtrip(
        lines,
        auto=True,
        redact=["token"],
        pattern=r"[\w.+-]+@[\w-]+\.[\w.]+",
    )
    assert result[0]["secret"] == REDACT_PLACEHOLDER
    assert result[0]["token"] == REDACT_PLACEHOLDER
    assert "user@x.com" not in result[0]["msg"]
