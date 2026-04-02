from __future__ import annotations

from collections.abc import Iterable


def detect_column(
    columns: Iterable[str],
    candidates: list[str],
    *,
    required: bool = True,
) -> str | None:
    column_map = {str(column): str(column) for column in columns}
    lower_map = {str(column).lower(): str(column) for column in columns}
    for candidate in candidates:
        if candidate in column_map:
            return column_map[candidate]
        lowered = candidate.lower()
        if lowered in lower_map:
            return lower_map[lowered]
    if required:
        raise ValueError(f"Could not find any of the expected columns: {', '.join(candidates)}")
    return None


def coerce_chromosome(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.removeprefix("chr").removeprefix("CHR")
