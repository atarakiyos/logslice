"""Simple ASCII table renderer for pivot / aggregation output."""

from typing import Any, List


def render_table(
    headers: List[str],
    rows: List[List[Any]],
    min_col_width: int = 4,
) -> str:
    """Render headers + rows as a plain ASCII table string.

    Parameters
    ----------
    headers:
        Column names.
    rows:
        Data rows; each row must have the same length as *headers*.
    min_col_width:
        Minimum width for every column.

    Returns
    -------
    str
        Multi-line string with a header row, separator, and data rows.
    """
    if not headers:
        return ""

    str_rows = [[str(cell) for cell in row] for row in rows]
    col_widths = [
        max(
            min_col_width,
            len(headers[i]),
            *(len(r[i]) for r in str_rows) if str_rows else [0],
        )
        for i in range(len(headers))
    ]

    def _fmt_row(cells: List[str]) -> str:
        return "| " + " | ".join(
            cell.ljust(col_widths[i]) for i, cell in enumerate(cells)
        ) + " |"

    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    lines = [
        sep,
        _fmt_row(headers),
        sep,
    ]
    for row in str_rows:
        lines.append(_fmt_row(row))
    lines.append(sep)
    return "\n".join(lines)


def render_counts(
    counts: dict,
    field_label: str = "value",
    count_label: str = "count",
) -> str:
    """Convenience wrapper: render a {value: count} dict as a two-column table."""
    headers = [field_label, count_label]
    rows = [[k, v] for k, v in sorted(counts.items(), key=lambda x: -x[1])]
    return render_table(headers, rows)
