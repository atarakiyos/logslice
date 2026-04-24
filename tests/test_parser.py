"""Tests for logslice.parser module."""

from datetime import datetime

import pytest

from logslice.parser import parse_line, parse_timestamp


class TestParseJsonLine:
    def test_basic_json(self):
        line = '{"level": "info", "msg": "hello", "ts": "2024-03-01T12:00:00Z"}'
        entry = parse_line(line)
        assert entry is not None
        assert entry["level"] == "info"
        assert entry["timestamp"] == "2024-03-01T12:00:00Z"

    def test_warn_normalized_to_warning(self):
        line = '{"lvl": "warn", "msg": "degraded"}'
        entry = parse_line(line)
        assert entry["level"] == "warning"

    def test_invalid_json_returns_none(self):
        assert parse_line("not json at all") is None

    def test_empty_line_returns_none(self):
        assert parse_line("") is None
        assert parse_line("   ") is None

    def test_json_array_returns_none(self):
        # We only accept dicts
        line = '["a", "b"]'
        assert parse_line(line) is None


class TestParseLogfmtLine:
    def test_basic_logfmt(self):
        line = 'level=info msg="user logged in" user=alice'
        entry = parse_line(line)
        assert entry is not None
        assert entry["level"] == "info"
        assert entry["msg"] == "user logged in"
        assert entry["user"] == "alice"

    def test_timestamp_normalization(self):
        line = "time=2024-03-01T10:00:00Z level=debug msg=boot"
        entry = parse_line(line)
        assert entry["timestamp"] == "2024-03-01T10:00:00Z"

    def test_severity_field(self):
        line = "severity=ERROR msg=failure"
        entry = parse_line(line)
        assert entry["level"] == "error"


class TestParseTimestamp:
    @pytest.mark.parametrize("ts,expected", [
        ("2024-03-01T12:00:00Z", datetime(2024, 3, 1, 12, 0, 0)),
        ("2024-03-01 12:00:00", datetime(2024, 3, 1, 12, 0, 0)),
        ("2024-03-01T12:00:00.123456Z", datetime(2024, 3, 1, 12, 0, 0, 123456)),
    ])
    def test_valid_timestamps(self, ts, expected):
        result = parse_timestamp(ts)
        assert result is not None
        assert result.replace(tzinfo=None) == expected

    def test_invalid_timestamp_returns_none(self):
        assert parse_timestamp("not-a-date") is None
