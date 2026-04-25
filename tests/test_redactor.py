"""Tests for logslice.redactor."""

import pytest
from logslice.redactor import (
    REDACT_PLACEHOLDER,
    auto_redact,
    apply_redaction,
    mask_field,
    redact_fields,
    redact_pattern,
)


def _e(**kwargs):
    return {"level": "INFO", "msg": "test", **kwargs}


# --- redact_fields ---

def test_redact_fields_replaces_value():
    entry = _e(password="s3cr3t")
    result = redact_fields(entry, ["password"])
    assert result["password"] == REDACT_PLACEHOLDER


def test_redact_fields_absent_key_unchanged():
    entry = _e(user="alice")
    result = redact_fields(entry, ["password"])
    assert result == entry


def test_redact_fields_does_not_mutate_original():
    entry = _e(token="abc123")
    redact_fields(entry, ["token"])
    assert entry["token"] == "abc123"


def test_redact_fields_multiple_fields():
    entry = _e(token="abc", secret="xyz", user="bob")
    result = redact_fields(entry, ["token", "secret"])
    assert result["token"] == REDACT_PLACEHOLDER
    assert result["secret"] == REDACT_PLACEHOLDER
    assert result["user"] == "bob"


# --- mask_field ---

def test_mask_field_preserves_last_chars():
    entry = _e(token="abcdef1234")
    result = mask_field(entry, "token", visible_chars=4)
    assert result["token"].endswith("1234")
    assert "*" in result["token"]


def test_mask_field_short_value_fully_masked():
    entry = _e(token="ab")
    result = mask_field(entry, "token", visible_chars=4)
    assert result["token"] == "**"


def test_mask_field_absent_key_unchanged():
    entry = _e(user="alice")
    result = mask_field(entry, "token")
    assert result == entry


# --- redact_pattern ---

def test_redact_pattern_replaces_match_in_string_field():
    entry = _e(msg="user email is alice@example.com here")
    result = redact_pattern(entry, r"[\w.+-]+@[\w-]+\.[\w.]+")
    assert "alice@example.com" not in result["msg"]
    assert REDACT_PLACEHOLDER in result["msg"]


def test_redact_pattern_skips_non_string_fields():
    entry = _e(count=42, msg="hello secret")
    result = redact_pattern(entry, r"secret")
    assert result["count"] == 42


# --- auto_redact ---

def test_auto_redact_removes_known_sensitive_keys():
    entry = _e(password="pass", token="tok", user="alice")
    result = auto_redact(entry)
    assert result["password"] == REDACT_PLACEHOLDER
    assert result["token"] == REDACT_PLACEHOLDER
    assert result["user"] == "alice"


def test_auto_redact_extra_keys():
    entry = _e(ssn="123-45-6789", user="bob")
    result = auto_redact(entry, extra_keys=["ssn"])
    assert result["ssn"] == REDACT_PLACEHOLDER


def test_auto_redact_case_insensitive():
    entry = _e(Password="hunter2")
    result = auto_redact(entry)
    assert result["Password"] == REDACT_PLACEHOLDER


# --- apply_redaction ---

def test_apply_redaction_redact_option():
    entries = [_e(token="abc"), _e(token="def")]
    result = apply_redaction(entries, redact=["token"])
    assert all(e["token"] == REDACT_PLACEHOLDER for e in result)


def test_apply_redaction_auto_flag():
    entries = [_e(secret="s", user="u")]
    result = apply_redaction(entries, auto=True)
    assert result[0]["secret"] == REDACT_PLACEHOLDER
    assert result[0]["user"] == "u"


def test_apply_redaction_empty_list():
    assert apply_redaction([]) == []
