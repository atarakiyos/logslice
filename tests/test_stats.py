"""Tests for logslice.stats module."""
import pytest
from datetime import datetime, timezone
from logslice.stats import compute_stats, format_stats


def _make_entry(level=None, ts=None, **extra):
    entry = {"message": "test"}
    if level:
        entry["level"] = level
    if ts:
        entry["timestamp"] = ts
    entry.update(extra)
    return entry


TS1 = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
TS2 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


class TestComputeStats:
    def test_empty_list(self):
        stats = compute_stats([])
        assert stats["total"] == 0
        assert stats["by_level"] == {}
        assert stats["earliest"] is None
        assert stats["latest"] is None
        assert stats["fields_seen"] == []

    def test_total_count(self):
        entries = [_make_entry(), _make_entry(), _make_entry()]
        stats = compute_stats(entries)
        assert stats["total"] == 3

    def test_level_counts_uppercased(self):
        entries = [
            _make_entry(level="info"),
            _make_entry(level="INFO"),
            _make_entry(level="error"),
        ]
        stats = compute_stats(entries)
        assert stats["by_level"]["INFO"] == 2
        assert stats["by_level"]["ERROR"] == 1

    def test_timestamps_earliest_latest(self):
        entries = [
            _make_entry(ts=TS2),
            _make_entry(ts=TS1),
        ]
        stats = compute_stats(entries)
        assert stats["earliest"] == TS1.isoformat()
        assert stats["latest"] == TS2.isoformat()

    def test_no_timestamps(self):
        entries = [_make_entry(level="debug")]
        stats = compute_stats(entries)
        assert stats["earliest"] is None
        assert stats["latest"] is None

    def test_fields_seen_sorted(self):
        entries = [
            _make_entry(level="info", service="web"),
            _make_entry(level="error", host="srv1"),
        ]
        stats = compute_stats(entries)
        assert "level" in stats["fields_seen"]
        assert "service" in stats["fields_seen"]
        assert "host" in stats["fields_seen"]
        assert stats["fields_seen"] == sorted(stats["fields_seen"])

    def test_missing_level_ignored(self):
        entries = [_make_entry(), _make_entry(level="warn")]
        stats = compute_stats(entries)
        assert stats["by_level"] == {"WARN": 1}


class TestFormatStats:
    def test_includes_total(self):
        stats = compute_stats([_make_entry(level="info")])
        output = format_stats(stats)
        assert "Total entries" in output
        assert "1" in output

    def test_includes_level_breakdown(self):
        entries = [_make_entry(level="error"), _make_entry(level="info")]
        output = format_stats(compute_stats(entries))
        assert "ERROR" in output
        assert "INFO" in output

    def test_na_when_no_timestamps(self):
        output = format_stats(compute_stats([_make_entry()]))
        assert "N/A" in output

    def test_empty_stats_renders(self):
        output = format_stats(compute_stats([]))
        assert "0" in output
