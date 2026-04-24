"""Tests for logslice.filters module."""

from datetime import datetime

import pytest

from logslice.filters import (
    apply_filters,
    filter_by_field_pattern,
    filter_by_level,
    filter_by_time_range,
)


ENTRY = {
    "level": "warning",
    "timestamp": "2024-03-01T10:30:00Z",
    "service": "auth",
    "msg": "failed login attempt",
}


class TestFilterByLevel:
    def test_passes_equal_level(self):
        assert filter_by_level(ENTRY, "warning") is True

    def test_passes_lower_minimum(self):
        assert filter_by_level(ENTRY, "info") is True

    def test_blocks_higher_minimum(self):
        assert filter_by_level(ENTRY, "error") is False

    def test_unknown_level_passes(self):
        entry = {"level": "trace"}
        assert filter_by_level(entry, "info") is True


class TestFilterByTimeRange:
    def test_within_range(self):
        start = datetime(2024, 3, 1, 10, 0, 0)
        end = datetime(2024, 3, 1, 11, 0, 0)
        assert filter_by_time_range(ENTRY, start, end) is True

    def test_before_start(self):
        start = datetime(2024, 3, 1, 11, 0, 0)
        assert filter_by_time_range(ENTRY, start, None) is False

    def test_after_end(self):
        end = datetime(2024, 3, 1, 10, 0, 0)
        assert filter_by_time_range(ENTRY, None, end) is False

    def test_no_range_passes(self):
        assert filter_by_time_range(ENTRY, None, None) is True

    def test_missing_timestamp_blocked(self):
        assert filter_by_time_range({"level": "info"}, datetime(2024, 1, 1), None) is False


class TestFilterByFieldPattern:
    def test_matching_pattern(self):
        assert filter_by_field_pattern(ENTRY, "service", "auth") is True

    def test_non_matching_pattern(self):
        assert filter_by_field_pattern(ENTRY, "service", "payment") is False

    def test_regex_pattern(self):
        assert filter_by_field_pattern(ENTRY, "msg", r"failed.*attempt") is True

    def test_missing_field_returns_false(self):
        assert filter_by_field_pattern(ENTRY, "nonexistent", ".*") is False

    def test_invalid_regex_returns_false(self):
        assert filter_by_field_pattern(ENTRY, "service", "[invalid") is False


class TestApplyFilters:
    def test_all_filters_pass(self):
        assert apply_filters(
            ENTRY,
            level="info",
            start=datetime(2024, 3, 1, 10, 0, 0),
            end=datetime(2024, 3, 1, 11, 0, 0),
            field_patterns={"service": "auth"},
        ) is True

    def test_level_filter_blocks(self):
        assert apply_filters(ENTRY, level="error") is False

    def test_no_filters_passes(self):
        assert apply_filters(ENTRY) is True
