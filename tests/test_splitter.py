"""Tests for logslice.splitter."""

from datetime import datetime, timedelta

import pytest

from logslice.splitter import split_by_count, split_by_field, split_by_time_window


def _ts(offset_seconds: float = 0) -> datetime:
    base = datetime(2024, 1, 1, 12, 0, 0)
    return base + timedelta(seconds=offset_seconds)


def _e(msg: str, ts: datetime | None = None, level: str = "INFO") -> dict:
    entry: dict = {"message": msg, "level": level}
    if ts is not None:
        entry["timestamp"] = ts
    return entry


# ---------------------------------------------------------------------------
# split_by_count
# ---------------------------------------------------------------------------

class TestSplitByCount:
    def test_even_split(self):
        entries = [_e(str(i)) for i in range(6)]
        chunks = list(split_by_count(entries, 2))
        assert len(chunks) == 3
        assert all(len(c) == 2 for c in chunks)

    def test_uneven_split_last_chunk_smaller(self):
        entries = [_e(str(i)) for i in range(5)]
        chunks = list(split_by_count(entries, 2))
        assert len(chunks) == 3
        assert len(chunks[-1]) == 1

    def test_chunk_larger_than_input_returns_one_chunk(self):
        entries = [_e("a"), _e("b")]
        chunks = list(split_by_count(entries, 100))
        assert len(chunks) == 1
        assert chunks[0] == entries

    def test_empty_input_yields_nothing(self):
        assert list(split_by_count([], 3)) == []

    def test_invalid_chunk_size_raises(self):
        with pytest.raises(ValueError):
            list(split_by_count([_e("x")], 0))


# ---------------------------------------------------------------------------
# split_by_time_window
# ---------------------------------------------------------------------------

class TestSplitByTimeWindow:
    def test_single_window_when_all_within_range(self):
        entries = [_e("a", _ts(0)), _e("b", _ts(5)), _e("c", _ts(9))]
        chunks = list(split_by_time_window(entries, window_seconds=10))
        assert len(chunks) == 1
        assert len(chunks[0]) == 3

    def test_splits_on_window_boundary(self):
        entries = [_e("a", _ts(0)), _e("b", _ts(10)), _e("c", _ts(20))]
        chunks = list(split_by_time_window(entries, window_seconds=10))
        assert len(chunks) == 3

    def test_entry_without_timestamp_stays_in_current_window(self):
        entries = [_e("a", _ts(0)), _e("no-ts"), _e("b", _ts(5))]
        chunks = list(split_by_time_window(entries, window_seconds=10))
        assert len(chunks) == 1
        assert len(chunks[0]) == 3

    def test_empty_input_yields_nothing(self):
        assert list(split_by_time_window([], window_seconds=60)) == []

    def test_invalid_window_raises(self):
        with pytest.raises(ValueError):
            list(split_by_time_window([_e("x", _ts())], window_seconds=0))


# ---------------------------------------------------------------------------
# split_by_field
# ---------------------------------------------------------------------------

class TestSplitByField:
    def test_groups_by_field_value(self):
        entries = [_e("a", level="ERROR"), _e("b", level="INFO"), _e("c", level="ERROR")]
        result = split_by_field(entries, field="level")
        assert set(result.keys()) == {"ERROR", "INFO"}
        assert len(result["ERROR"]) == 2
        assert len(result["INFO"]) == 1

    def test_missing_field_uses_sentinel(self):
        entries = [_e("a"), {"message": "no-level"}]
        result = split_by_field(entries, field="level")
        assert "__missing__" in result

    def test_custom_sentinel(self):
        result = split_by_field([{"msg": "hi"}], field="level", sentinel="N/A")
        assert "N/A" in result

    def test_empty_input_returns_empty_dict(self):
        assert split_by_field([], field="level") == {}
