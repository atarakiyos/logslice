"""Pivot table generation for log entries grouped by one or two fields."""

from typing import Any, Dict, List, Optional, Tuple

from logslice.aggregator import count_by_field, group_by_field


def build_pivot(
    entries: List[Dict[str, Any]],
    row_field: str,
    col_field: str,
) -> Dict[str, Dict[str, int]]:
    """Build a 2-D pivot table: rows keyed by row_field, cols by col_field.

    Each cell contains the count of entries matching that combination.
    """
    pivot: Dict[str, Dict[str, int]] = {}
    row_groups = group_by_field(entries, row_field)
    for row_val, row_entries in row_groups.items():
        pivot[row_val] = count_by_field(row_entries, col_field)
    return pivot


def pivot_to_rows(
    pivot: Dict[str, Dict[str, int]],
    col_order: Optional[List[str]] = None,
) -> Tuple[List[str], List[List[Any]]]:
    """Flatten a pivot dict into (headers, rows) for tabular display.

    Parameters
    ----------
    pivot:
        Output of :func:`build_pivot`.
    col_order:
        Optional explicit column ordering.  Unknown columns are appended.

    Returns
    -------
    headers:
        List of column names starting with "row_key".
    rows:
        List of rows where each row is [row_key, col1_count, col2_count, ...].
    """
    all_cols: List[str] = []
    for col_counts in pivot.values():
        for col in col_counts:
            if col not in all_cols:
                all_cols.append(col)

    if col_order:
        ordered = [c for c in col_order if c in all_cols]
        remaining = [c for c in all_cols if c not in ordered]
        all_cols = ordered + remaining

    headers = ["row_key"] + all_cols
    rows: List[List[Any]] = []
    for row_key in sorted(pivot.keys()):
        col_counts = pivot[row_key]
        row = [row_key] + [col_counts.get(col, 0) for col in all_cols]
        rows.append(row)

    return headers, rows
