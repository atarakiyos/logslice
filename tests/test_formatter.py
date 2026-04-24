"""Tests for logslice.formatter output formatting helpers."""

import json
import pytest
from logslice.formatter import (
    format_json,
    format_logfmt,
    format_pretty,
    format_entry,
    SUPPORTED_FORMATS,
)

SAMPLE_ENTRY = {
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "info",
    "message": "server started",
    "port": 8080,
}


class TestFormatJson:
    def test_produces_valid_json(self):
        result = format_json(SAMPLE_ENTRY)
        parsed = json.loads(result)
        assert parsed["level"] == "info"

    def test_compact_no_newlines(self):
        result = format_json(SAMPLE_ENTRY)
        assert "\n" not in result

    def test_integer_values_preserved(self):
        result = format_json(SAMPLE_ENTRY)
        assert '"port": 8080' in result or '"port":8080' in result


class TestFormatLogfmt:
    def test_contains_key_value_pairs(self):
        result = format_logfmt(SAMPLE_ENTRY)
        assert "level=info" in result
        assert "port=8080" in result

    def test_quotes_values_with_spaces(self):
        entry = {"message": "hello world", "level": "info"}
        result = format_logfmt(entry)
        assert 'message="hello world"' in result

    def test_no_spaces_in_simple_values(self):
        entry = {"level": "warning"}
        result = format_logfmt(entry)
        assert result == "level=warning"


class TestFormatPretty:
    def test_contains_level_uppercased(self):
        result = format_pretty(SAMPLE_ENTRY)
        assert "INFO" in result

    def test_contains_message(self):
        result = format_pretty(SAMPLE_ENTRY)
        assert "server started" in result

    def test_contains_timestamp(self):
        result = format_pretty(SAMPLE_ENTRY)
        assert "2024-01-15T10:30:00Z" in result

    def test_extra_fields_appended(self):
        result = format_pretty(SAMPLE_ENTRY)
        assert "port=8080" in result

    def test_no_extras_no_trailing_spaces(self):
        entry = {"timestamp": "2024-01-15T10:30:00Z", "level": "info", "message": "ok"}
        result = format_pretty(entry)
        assert result.endswith("ok")


class TestFormatEntry:
    def test_json_format(self):
        result = format_entry(SAMPLE_ENTRY, fmt="json")
        assert json.loads(result)["level"] == "info"

    def test_logfmt_format(self):
        result = format_entry(SAMPLE_ENTRY, fmt="logfmt")
        assert "level=info" in result

    def test_pretty_format(self):
        result = format_entry(SAMPLE_ENTRY, fmt="pretty")
        assert "INFO" in result

    def test_unsupported_format_returns_none(self):
        result = format_entry(SAMPLE_ENTRY, fmt="xml")
        assert result is None

    def test_default_format_is_json(self):
        result = format_entry(SAMPLE_ENTRY)
        assert result is not None
        assert json.loads(result) is not None


def test_supported_formats_contains_expected():
    for fmt in ("json", "logfmt", "pretty"):
        assert fmt in SUPPORTED_FORMATS
