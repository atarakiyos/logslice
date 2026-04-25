"""Tests for logslice.highlighter."""

from __future__ import annotations

import re

import pytest

from logslice.highlighter import (
    highlight_entry,
    highlight_level,
    highlight_pattern,
)

_ANSI_RE = re.compile(r"\033\[[0-9;]+m")


def _strip(text: str) -> str:
    """Remove ANSI escape sequences from *text*."""
    return _ANSI_RE.sub("", text)


# ---------------------------------------------------------------------------
# highlight_level
# ---------------------------------------------------------------------------

class TestHighlightLevel:
    def test_error_contains_ansi(self):
        result = highlight_level("ERROR")
        assert "\033[" in result

    def test_error_plain_text_preserved(self):
        assert _strip(highlight_level("ERROR")) == "ERROR"

    def test_warning_plain_text_preserved(self):
        assert _strip(highlight_level("warning")) == "WARNING"

    def test_info_plain_text_preserved(self):
        assert _strip(highlight_level("info")) == "INFO"

    def test_unknown_level_returned_unchanged(self):
        assert highlight_level("TRACE") == "TRACE"

    def test_none_returns_empty_string(self):
        assert highlight_level(None) == ""


# ---------------------------------------------------------------------------
# highlight_pattern
# ---------------------------------------------------------------------------

class TestHighlightPattern:
    def test_match_is_wrapped(self):
        result = highlight_pattern("hello world", "world")
        assert "\033[" in result
        assert _strip(result) == "hello world"

    def test_no_match_unchanged(self):
        result = highlight_pattern("hello world", "xyz")
        assert result == "hello world"

    def test_invalid_regex_returns_original(self):
        result = highlight_pattern("hello", "[invalid")
        assert result == "hello"

    def test_multiple_matches_all_highlighted(self):
        result = highlight_pattern("aaa", "a")
        # Three separate colour wraps expected
        assert _strip(result) == "aaa"
        assert result.count("\033[") >= 3


# ---------------------------------------------------------------------------
# highlight_entry
# ---------------------------------------------------------------------------

class TestHighlightEntry:
    def _entry(self, **kwargs):
        base = {"timestamp": "2024-01-01T00:00:00Z", "level": "INFO", "message": "hello"}
        base.update(kwargs)
        return base

    def test_plain_text_contains_all_fields(self):
        result = _strip(highlight_entry(self._entry()))
        assert "2024-01-01T00:00:00Z" in result
        assert "INFO" in result
        assert "hello" in result

    def test_pattern_highlights_message(self):
        result = highlight_entry(self._entry(message="error occurred"), pattern="error")
        assert "\033[" in result
        assert _strip(result).count("error") == 1

    def test_missing_message_uses_msg_key(self):
        entry = {"level": "DEBUG", "msg": "fallback"}
        result = _strip(highlight_entry(entry))
        assert "fallback" in result

    def test_empty_entry_no_crash(self):
        result = highlight_entry({})
        assert isinstance(result, str)
