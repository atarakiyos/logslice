"""Tests for logslice.deduplicator."""

import pytest

from logslice.deduplicator import (
    _entry_fingerprint,
    count_duplicates,
    deduplicate,
)


def _e(msg: str, level: str = "INFO", extra: dict | None = None) -> dict:
    entry = {"message": msg, "level": level}
    if extra:
        entry.update(extra)
    return entry


# ---------------------------------------------------------------------------
# _entry_fingerprint
# ---------------------------------------------------------------------------

class TestEntryFingerprint:
    def test_same_entry_same_fingerprint(self):
        e = _e("hello")
        assert _entry_fingerprint(e) == _entry_fingerprint(e)

    def test_different_entries_different_fingerprint(self):
        assert _entry_fingerprint(_e("a")) != _entry_fingerprint(_e("b"))

    def test_raw_field_excluded(self):
        e1 = {"message": "hi", "level": "INFO"}
        e2 = {"message": "hi", "level": "INFO", "_raw": "original text"}
        assert _entry_fingerprint(e1) == _entry_fingerprint(e2)

    def test_field_subset_ignores_other_keys(self):
        e1 = _e("hello", extra={"host": "a"})
        e2 = _e("hello", extra={"host": "b"})
        # Only compare on 'message' — host difference should be ignored
        assert _entry_fingerprint(e1, fields=["message"]) == _entry_fingerprint(
            e2, fields=["message"]
        )


# ---------------------------------------------------------------------------
# deduplicate — keep='first'
# ---------------------------------------------------------------------------

class TestDeduplicateFirst:
    def test_no_duplicates_unchanged(self):
        entries = [_e("a"), _e("b"), _e("c")]
        assert list(deduplicate(entries)) == entries

    def test_exact_duplicates_removed(self):
        entries = [_e("x"), _e("x"), _e("x")]
        result = list(deduplicate(entries))
        assert result == [_e("x")]

    def test_keeps_first_occurrence(self):
        e1 = {"message": "dup", "level": "INFO", "seq": 1}
        e2 = {"message": "dup", "level": "INFO", "seq": 1}
        e1_copy = dict(e1)  # identical content
        result = list(deduplicate([e1, e2]))
        assert len(result) == 1

    def test_partial_field_dedup(self):
        e1 = _e("msg", extra={"host": "a"})
        e2 = _e("msg", extra={"host": "b"})
        # Deduplicate only on 'message' field — both share same message
        result = list(deduplicate([e1, e2], fields=["message"]))
        assert result == [e1]


# ---------------------------------------------------------------------------
# deduplicate — keep='last'
# ---------------------------------------------------------------------------

class TestDeduplicateLast:
    def test_keeps_last_occurrence(self):
        e1 = {"message": "dup", "level": "INFO"}
        e2 = {"message": "dup", "level": "INFO"}
        result = list(deduplicate([e1, e2], keep="last"))
        assert len(result) == 1
        assert result[0] is e2

    def test_invalid_keep_raises(self):
        with pytest.raises(ValueError, match="keep"):
            list(deduplicate([_e("a")], keep="middle"))


# ---------------------------------------------------------------------------
# count_duplicates
# ---------------------------------------------------------------------------

class TestCountDuplicates:
    def test_no_duplicates_returns_zero(self):
        entries = [_e("a"), _e("b"), _e("c")]
        assert count_duplicates(entries) == 0

    def test_counts_duplicate_entries(self):
        entries = [_e("x"), _e("x"), _e("x"), _e("y"), _e("y")]
        # 2 extra 'x' + 1 extra 'y' = 3 duplicates
        assert count_duplicates(entries) == 3

    def test_single_entry_no_duplicates(self):
        assert count_duplicates([_e("only")]) == 0

    def test_empty_input_returns_zero(self):
        assert count_duplicates([]) == 0
