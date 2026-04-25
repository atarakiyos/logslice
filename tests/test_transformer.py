"""Tests for logslice.transformer."""

import pytest
from logslice.transformer import (
    rename_field,
    drop_fields,
    keep_fields,
    apply_transform,
    add_field,
    coerce_field_to_int,
    coerce_field_to_float,
)


def _e(**kwargs):
    return {"raw": "", **kwargs}


# --- rename_field ---

def test_rename_field_present():
    entries = [_e(msg="hello")]
    result = rename_field(entries, "msg", "message")
    assert "message" in result[0]
    assert "msg" not in result[0]
    assert result[0]["message"] == "hello"


def test_rename_field_absent_unchanged():
    entries = [_e(level="info")]
    result = rename_field(entries, "msg", "message")
    assert result[0] == entries[0]


def test_rename_field_empty_list():
    assert rename_field([], "a", "b") == []


# --- drop_fields ---

def test_drop_fields_removes_specified():
    entries = [_e(level="info", msg="hi", ts="2024-01-01")]
    result = drop_fields(entries, ["level", "ts"])
    assert "level" not in result[0]
    assert "ts" not in result[0]
    assert result[0]["msg"] == "hi"


def test_drop_fields_missing_field_ok():
    entries = [_e(level="info")]
    result = drop_fields(entries, ["nonexistent"])
    assert result[0]["level"] == "info"


# --- keep_fields ---

def test_keep_fields_retains_only_specified():
    entries = [_e(level="info", msg="hi", ts="2024-01-01")]
    result = keep_fields(entries, ["level"])
    assert "level" in result[0]
    assert "msg" not in result[0]
    assert "ts" not in result[0]


def test_keep_fields_always_keeps_raw():
    entries = [_e(level="info")]
    result = keep_fields(entries, ["level"])
    assert "raw" in result[0]


# --- apply_transform ---

def test_apply_transform_modifies_field():
    entries = [_e(msg="hello")]
    result = apply_transform(entries, "msg", str.upper)
    assert result[0]["msg"] == "HELLO"


def test_apply_transform_error_leaves_original():
    entries = [_e(count="not_a_number")]
    result = apply_transform(entries, "count", int)
    assert result[0]["count"] == "not_a_number"


# --- add_field ---

def test_add_field_when_absent():
    entries = [_e(level="info")]
    result = add_field(entries, "env", "production")
    assert result[0]["env"] == "production"


def test_add_field_does_not_overwrite():
    entries = [_e(env="staging")]
    result = add_field(entries, "env", "production")
    assert result[0]["env"] == "staging"


# --- coerce helpers ---

def test_coerce_field_to_int():
    entries = [_e(status="200")]
    result = coerce_field_to_int(entries, "status")
    assert result[0]["status"] == 200
    assert isinstance(result[0]["status"], int)


def test_coerce_field_to_float():
    entries = [_e(duration="1.23")]
    result = coerce_field_to_float(entries, "duration")
    assert abs(result[0]["duration"] - 1.23) < 1e-9
