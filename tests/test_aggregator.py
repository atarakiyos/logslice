"""Tests for logslice.aggregator."""

import pytest
from logslice.aggregator import (
    aggregate_numeric_field,
    count_by_field,
    group_by_field,
    top_values,
)


def _e(**kwargs):
    return {"level": "INFO", "msg": "test", **kwargs}


# ---------------------------------------------------------------------------
# group_by_field
# ---------------------------------------------------------------------------

class TestGroupByField:
    def test_groups_correctly(self):
        entries = [_e(service="web"), _e(service="db"), _e(service="web")]
        groups = group_by_field(entries, "service")
        assert len(groups["web"]) == 2
        assert len(groups["db"]) == 1

    def test_missing_field_uses_sentinel(self):
        entries = [_e(), _e(service="web")]
        groups = group_by_field(entries, "service")
        assert "__missing__" in groups
        assert len(groups["__missing__"]) == 1

    def test_empty_input(self):
        assert group_by_field([], "service") == {}

    def test_single_group(self):
        entries = [_e(env="prod")] * 4
        groups = group_by_field(entries, "env")
        assert list(groups.keys()) == ["prod"]
        assert len(groups["prod"]) == 4


# ---------------------------------------------------------------------------
# count_by_field
# ---------------------------------------------------------------------------

class TestCountByField:
    def test_basic_counts(self):
        entries = [_e(level="ERROR"), _e(level="INFO"), _e(level="ERROR")]
        counts = count_by_field(entries, "level")
        assert counts["ERROR"] == 2
        assert counts["INFO"] == 1

    def test_empty_input(self):
        assert count_by_field([], "level") == {}

    def test_missing_values_counted(self):
        entries = [_e(), _e()]
        counts = count_by_field(entries, "nonexistent")
        assert counts["__missing__"] == 2


# ---------------------------------------------------------------------------
# top_values
# ---------------------------------------------------------------------------

def test_top_values_sorted_descending():
    counts = {"a": 1, "b": 5, "c": 3}
    result = top_values(counts, n=2)
    assert result[0] == ("b", 5)
    assert result[1] == ("c", 3)


def test_top_values_n_larger_than_dict():
    counts = {"x": 2}
    result = top_values(counts, n=10)
    assert len(result) == 1


def test_top_values_empty():
    assert top_values({}) == []


# ---------------------------------------------------------------------------
# aggregate_numeric_field
# ---------------------------------------------------------------------------

class TestAggregateNumericField:
    def test_basic_stats(self):
        entries = [_e(duration=10), _e(duration=20), _e(duration=30)]
        result = aggregate_numeric_field(entries, "duration")
        assert result["min"] == 10.0
        assert result["max"] == 30.0
        assert result["mean"] == 20.0
        assert result["count"] == 3.0

    def test_no_numeric_values_returns_none(self):
        entries = [_e(duration="fast"), _e()]
        assert aggregate_numeric_field(entries, "duration") is None

    def test_empty_entries_returns_none(self):
        assert aggregate_numeric_field([], "duration") is None

    def test_string_numbers_parsed(self):
        entries = [_e(latency="1.5"), _e(latency="2.5")]
        result = aggregate_numeric_field(entries, "latency")
        assert result is not None
        assert result["mean"] == pytest.approx(2.0)

    def test_mixed_valid_invalid_skips_invalid(self):
        entries = [_e(size=100), _e(size="N/A"), _e(size=200)]
        result = aggregate_numeric_field(entries, "size")
        assert result["count"] == 2.0
        assert result["mean"] == 150.0
