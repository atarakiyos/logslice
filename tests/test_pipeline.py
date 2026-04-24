"""Tests for logslice.pipeline module."""
import json
import io
import pytest
from datetime import datetime, timezone
from logslice.pipeline import run_pipeline, run_pipeline_from_file


def _json_line(**kwargs) -> str:
    return json.dumps(kwargs)


TS_EARLY = "2024-01-01T08:00:00+00:00"
TS_MID = "2024-01-01T12:00:00+00:00"
TS_LATE = "2024-01-01T18:00:00+00:00"


class TestRunPipeline:
    def test_empty_input(self):
        assert run_pipeline([]) == []

    def test_invalid_lines_skipped(self):
        lines = ["not json at all", "{bad}", ""]
        assert run_pipeline(lines) == []

    def test_valid_lines_returned(self):
        lines = [
            _json_line(level="info", message="hello", timestamp=TS_MID),
            _json_line(level="error", message="boom", timestamp=TS_MID),
        ]
        result = run_pipeline(lines)
        assert len(result) == 2

    def test_min_level_filters(self):
        lines = [
            _json_line(level="debug", message="verbose", timestamp=TS_MID),
            _json_line(level="error", message="critical", timestamp=TS_MID),
        ]
        result = run_pipeline(lines, min_level="warning")
        assert len(result) == 1
        assert result[0]["level"] == "error"

    def test_time_range_filters(self):
        lines = [
            _json_line(level="info", message="early", timestamp=TS_EARLY),
            _json_line(level="info", message="mid", timestamp=TS_MID),
            _json_line(level="info", message="late", timestamp=TS_LATE),
        ]
        start = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 14, 0, tzinfo=timezone.utc)
        result = run_pipeline(lines, start=start, end=end)
        assert len(result) == 1
        assert result[0]["message"] == "mid"

    def test_field_pattern_filters(self):
        lines = [
            _json_line(level="info", message="hello world", timestamp=TS_MID),
            _json_line(level="info", message="goodbye", timestamp=TS_MID),
        ]
        result = run_pipeline(lines, field_patterns={"message": "hello"})
        assert len(result) == 1
        assert result[0]["message"] == "hello world"

    def test_mixed_valid_invalid_lines(self):
        lines = [
            _json_line(level="info", message="ok", timestamp=TS_MID),
            "garbage line",
            _json_line(level="info", message="also ok", timestamp=TS_MID),
        ]
        result = run_pipeline(lines)
        assert len(result) == 2


class TestRunPipelineFromFile:
    def test_reads_from_file_handle(self):
        content = "\n".join([
            _json_line(level="info", message="line1", timestamp=TS_MID),
            _json_line(level="warn", message="line2", timestamp=TS_MID),
        ])
        fh = io.StringIO(content)
        result = run_pipeline_from_file(fh)
        assert len(result) == 2

    def test_file_with_filter(self):
        content = "\n".join([
            _json_line(level="debug", message="noisy", timestamp=TS_MID),
            _json_line(level="error", message="important", timestamp=TS_MID),
        ])
        fh = io.StringIO(content)
        result = run_pipeline_from_file(fh, min_level="error")
        assert len(result) == 1
