"""Tests for logslice.exporter."""

from __future__ import annotations

import csv
import io
import json

import pytest

from logslice.exporter import (
    export_csv,
    export_entries,
    export_ndjson,
    export_tsv,
    _collect_fields,
)


def _e(**kwargs) -> dict:
    return {"raw": "", **kwargs}


# ---------------------------------------------------------------------------
# _collect_fields
# ---------------------------------------------------------------------------

def test_collect_fields_excludes_raw():
    entries = [_e(level="INFO", msg="hi")]
    assert "raw" not in _collect_fields(entries)


def test_collect_fields_union_of_all_entries():
    entries = [_e(a="1"), _e(b="2")]
    fields = _collect_fields(entries)
    assert "a" in fields and "b" in fields


def test_collect_fields_stable_order():
    entries = [_e(z="1", a="2", m="3")]
    fields = _collect_fields(entries)
    assert fields == ["z", "a", "m"]


# ---------------------------------------------------------------------------
# export_csv
# ---------------------------------------------------------------------------

def test_csv_empty_returns_empty_string():
    assert export_csv([]) == ""


def test_csv_header_row_present():
    entries = [_e(level="INFO", msg="hello")]
    output = export_csv(entries)
    reader = csv.DictReader(io.StringIO(output))
    assert set(reader.fieldnames or []) == {"level", "msg"}


def test_csv_values_correct():
    entries = [_e(level="ERROR", msg="boom")]
    output = export_csv(entries)
    rows = list(csv.DictReader(io.StringIO(output)))
    assert rows[0]["level"] == "ERROR"
    assert rows[0]["msg"] == "boom"


def test_csv_missing_field_is_empty_string():
    entries = [_e(level="INFO"), _e(level="WARN", msg="hi")]
    output = export_csv(entries)
    rows = list(csv.DictReader(io.StringIO(output)))
    assert rows[0].get("msg", "") == ""


# ---------------------------------------------------------------------------
# export_ndjson
# ---------------------------------------------------------------------------

def test_ndjson_empty_returns_empty_string():
    assert export_ndjson([]) == ""


def test_ndjson_each_line_is_valid_json():
    entries = [_e(level="INFO", msg="a"), _e(level="WARN", msg="b")]
    output = export_ndjson(entries)
    lines = [l for l in output.strip().splitlines() if l]
    assert len(lines) == 2
    for line in lines:
        obj = json.loads(line)
        assert "level" in obj


def test_ndjson_raw_excluded():
    entries = [_e(level="DEBUG", msg="x")]
    output = export_ndjson(entries)
    obj = json.loads(output.strip())
    assert "raw" not in obj


# ---------------------------------------------------------------------------
# export_tsv
# ---------------------------------------------------------------------------

def test_tsv_empty_returns_empty_string():
    assert export_tsv([]) == ""


def test_tsv_tab_delimited():
    entries = [_e(level="INFO", msg="ok")]
    output = export_tsv(entries)
    lines = output.splitlines()
    assert "\t" in lines[0]


# ---------------------------------------------------------------------------
# export_entries dispatch
# ---------------------------------------------------------------------------

def test_dispatch_csv():
    entries = [_e(level="INFO")]
    result = export_entries(entries, fmt="csv")
    assert "level" in result


def test_dispatch_ndjson():
    entries = [_e(level="INFO")]
    result = export_entries(entries, fmt="ndjson")
    assert json.loads(result.strip())["level"] == "INFO"


def test_dispatch_unknown_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        export_entries([], fmt="xml")
