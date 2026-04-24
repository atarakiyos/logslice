"""Tests for logslice.pivot."""

from logslice.pivot import build_pivot, pivot_to_rows


def _e(service, level):
    return {"service": service, "level": level, "msg": "x"}


ENTRIES = [
    _e("web", "INFO"),
    _e("web", "ERROR"),
    _e("web", "INFO"),
    _e("db", "INFO"),
    _e("db", "WARN"),
]


class TestBuildPivot:
    def test_row_keys_present(self):
        pivot = build_pivot(ENTRIES, "service", "level")
        assert "web" in pivot
        assert "db" in pivot

    def test_cell_counts(self):
        pivot = build_pivot(ENTRIES, "service", "level")
        assert pivot["web"]["INFO"] == 2
        assert pivot["web"]["ERROR"] == 1
        assert pivot["db"]["INFO"] == 1
        assert pivot["db"]["WARN"] == 1

    def test_missing_cell_absent(self):
        pivot = build_pivot(ENTRIES, "service", "level")
        assert "WARN" not in pivot["web"]

    def test_empty_entries(self):
        assert build_pivot([], "service", "level") == {}

    def test_missing_field_uses_sentinel(self):
        entries = [{"level": "INFO", "msg": "x"}]
        pivot = build_pivot(entries, "service", "level")
        assert "__missing__" in pivot


class TestPivotToRows:
    def test_headers_start_with_row_key(self):
        pivot = build_pivot(ENTRIES, "service", "level")
        headers, _ = pivot_to_rows(pivot)
        assert headers[0] == "row_key"

    def test_all_columns_in_headers(self):
        pivot = build_pivot(ENTRIES, "service", "level")
        headers, _ = pivot_to_rows(pivot)
        assert "INFO" in headers
        assert "ERROR" in headers
        assert "WARN" in headers

    def test_rows_sorted_by_row_key(self):
        pivot = build_pivot(ENTRIES, "service", "level")
        _, rows = pivot_to_rows(pivot)
        row_keys = [r[0] for r in rows]
        assert row_keys == sorted(row_keys)

    def test_zero_fill_for_missing_cells(self):
        pivot = build_pivot(ENTRIES, "service", "level")
        headers, rows = pivot_to_rows(pivot)
        warn_idx = headers.index("WARN")
        web_row = next(r for r in rows if r[0] == "web")
        assert web_row[warn_idx] == 0

    def test_col_order_respected(self):
        pivot = build_pivot(ENTRIES, "service", "level")
        headers, _ = pivot_to_rows(pivot, col_order=["ERROR", "INFO"])
        assert headers[1] == "ERROR"
        assert headers[2] == "INFO"

    def test_empty_pivot(self):
        headers, rows = pivot_to_rows({})
        assert headers == ["row_key"]
        assert rows == []
