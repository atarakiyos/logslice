"""Tests for logslice.redact_cmd."""

import json
import argparse
import pytest

from logslice.redact_cmd import build_redact_parser, run_redact_cmd
from logslice.redactor import REDACT_PLACEHOLDER


def _args(**kwargs):
    defaults = dict(
        input="-",
        redact=[],
        mask=None,
        pattern=None,
        auto=False,
        fmt="json",
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _json_line(**kwargs):
    base = {"level": "INFO", "msg": "hello"}
    base.update(kwargs)
    return json.dumps(base) + "\n"


def _run(lines, **kwargs):
    """Run the redact command and capture stdout via capsys workaround."""
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run_redact_cmd(_args(**kwargs), lines=lines)
    return [json.loads(l) for l in buf.getvalue().splitlines() if l.strip()]


def test_redact_single_field():
    lines = [_json_line(token="secret123")]
    result = _run(lines, redact=["token"])
    assert result[0]["token"] == REDACT_PLACEHOLDER


def test_redact_preserves_other_fields():
    lines = [_json_line(token="abc", user="alice")]
    result = _run(lines, redact=["token"])
    assert result[0]["user"] == "alice"


def test_mask_field_output():
    lines = [_json_line(token="abcdef1234")]
    result = _run(lines, mask="token")
    assert result[0]["token"].endswith("1234")
    assert "*" in result[0]["token"]


def test_auto_redacts_password():
    lines = [_json_line(password="hunter2", user="bob")]
    result = _run(lines, auto=True)
    assert result[0]["password"] == REDACT_PLACEHOLDER
    assert result[0]["user"] == "bob"


def test_pattern_redacts_email():
    lines = [_json_line(msg="contact alice@example.com please")]
    result = _run(lines, pattern=r"[\w.+-]+@[\w-]+\.[\w.]+")
    assert "alice@example.com" not in result[0]["msg"]


def test_invalid_lines_skipped():
    lines = ["not json at all\n", _json_line(token="x")]
    result = _run(lines, redact=["token"])
    assert len(result) == 1


def test_empty_input_produces_no_output():
    result = _run([], redact=["token"])
    assert result == []


def test_build_redact_parser_returns_parser():
    parser = build_redact_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_redact_parser_subparser():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    parser = build_redact_parser(sub)
    assert parser is not None
