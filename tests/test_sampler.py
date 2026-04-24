"""Tests for logslice.sampler."""

import pytest
from logslice.sampler import sample_by_rate, sample_by_count, sample_by_field_hash


def _make_entries(n: int):
    return [{"msg": f"line {i}", "index": i} for i in range(n)]


# ---------------------------------------------------------------------------
# sample_by_rate
# ---------------------------------------------------------------------------

class TestSampleByRate:
    def test_rate_one_returns_all(self):
        entries = _make_entries(10)
        assert sample_by_rate(entries, 1.0) == entries

    def test_rate_half_returns_half(self):
        entries = _make_entries(10)
        result = sample_by_rate(entries, 0.5)
        assert len(result) == 5

    def test_rate_preserves_order(self):
        entries = _make_entries(9)
        result = sample_by_rate(entries, 1 / 3)
        indices = [e["index"] for e in result]
        assert indices == sorted(indices)

    def test_invalid_rate_zero_raises(self):
        with pytest.raises(ValueError):
            sample_by_rate(_make_entries(5), 0.0)

    def test_invalid_rate_above_one_raises(self):
        with pytest.raises(ValueError):
            sample_by_rate(_make_entries(5), 1.5)

    def test_empty_input(self):
        assert sample_by_rate([], 0.5) == []


# ---------------------------------------------------------------------------
# sample_by_count
# ---------------------------------------------------------------------------

class TestSampleByCount:
    def test_count_greater_than_total_returns_all(self):
        entries = _make_entries(5)
        assert sample_by_count(entries, 100) == entries

    def test_exact_count_returned(self):
        entries = _make_entries(100)
        result = sample_by_count(entries, 10)
        assert len(result) == 10

    def test_count_one_returns_first(self):
        entries = _make_entries(10)
        result = sample_by_count(entries, 1)
        assert len(result) == 1
        assert result[0]["index"] == 0

    def test_invalid_count_raises(self):
        with pytest.raises(ValueError):
            sample_by_count(_make_entries(5), 0)

    def test_empty_input(self):
        assert sample_by_count([], 5) == []


# ---------------------------------------------------------------------------
# sample_by_field_hash
# ---------------------------------------------------------------------------

class TestSampleByFieldHash:
    def _entries_with_ids(self, n: int):
        return [{"request_id": f"req-{i}", "index": i} for i in range(n)]

    def test_rate_one_returns_all(self):
        entries = self._entries_with_ids(20)
        result = sample_by_field_hash(entries, "request_id", 1.0)
        assert result == entries

    def test_reduces_volume(self):
        entries = self._entries_with_ids(200)
        result = sample_by_field_hash(entries, "request_id", 0.1)
        assert len(result) < len(entries)

    def test_deterministic(self):
        entries = self._entries_with_ids(50)
        r1 = sample_by_field_hash(entries, "request_id", 0.5)
        r2 = sample_by_field_hash(entries, "request_id", 0.5)
        assert r1 == r2

    def test_missing_field_treated_as_empty_string(self):
        entries = [{"msg": "no id"}] * 10
        result = sample_by_field_hash(entries, "request_id", 0.5)
        assert isinstance(result, list)

    def test_invalid_rate_raises(self):
        with pytest.raises(ValueError):
            sample_by_field_hash([], "field", 0.0)
