"""Tests for logslice.writer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from logslice.writer import write_export, _fmt_from_path


def _e(**kwargs):
    return {"raw": "", **kwargs}


# ---------------------------------------------------------------------------
# _fmt_from_path
# ---------------------------------------------------------------------------

def test_csv_extension_detected():
    assert _fmt_from_path(Path("out.csv")) == "csv"


def test_tsv_extension_detected():
    assert _fmt_from_path(Path("out.tsv")) == "tsv"


def test_ndjson_extension_detected():
    assert _fmt_from_path(Path("out.ndjson")) == "ndjson"


def test_jsonl_extension_detected():
    assert _fmt_from_path(Path("out.jsonl")) == "ndjson"


def test_unknown_extension_defaults_to_ndjson():
    assert _fmt_from_path(Path("out.log")) == "ndjson"


# ---------------------------------------------------------------------------
# write_export — stdout
# ---------------------------------------------------------------------------

def test_stdout_ndjson(capsys):
    entries = [_e(level="INFO", msg="hello")]
    write_export(entries, dest=None, fmt="ndjson")
    captured = capsys.readouterr()
    obj = json.loads(captured.out.strip())
    assert obj["level"] == "INFO"


def test_stdout_csv(capsys):
    entries = [_e(level="ERROR")]
    write_export(entries, dest=None, fmt="csv")
    captured = capsys.readouterr()
    assert "level" in captured.out
    assert "ERROR" in captured.out


def test_stdout_default_fmt_is_ndjson(capsys):
    entries = [_e(level="DEBUG")]
    write_export(entries)  # no dest, no fmt
    captured = capsys.readouterr()
    obj = json.loads(captured.out.strip())
    assert "level" in obj


# ---------------------------------------------------------------------------
# write_export — file
# ---------------------------------------------------------------------------

def test_writes_csv_file(tmp_path):
    dest = str(tmp_path / "out.csv")
    entries = [_e(level="WARN", msg="watch out")]
    write_export(entries, dest=dest)
    content = Path(dest).read_text()
    assert "WARN" in content


def test_writes_ndjson_file(tmp_path):
    dest = str(tmp_path / "out.ndjson")
    entries = [_e(level="INFO", msg="ok")]
    write_export(entries, dest=dest)
    obj = json.loads(Path(dest).read_text().strip())
    assert obj["msg"] == "ok"


def test_fmt_override_beats_extension(tmp_path):
    """Explicit fmt= should win over file extension inference."""
    dest = str(tmp_path / "out.csv")  # extension says csv
    entries = [_e(level="INFO", msg="test")]
    write_export(entries, dest=dest, fmt="ndjson")  # but we force ndjson
    obj = json.loads(Path(dest).read_text().strip())
    assert obj["level"] == "INFO"
