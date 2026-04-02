from __future__ import annotations

import shutil
from pathlib import Path


def is_pre_munged_prefix(prefix: Path) -> bool:
    rows_path = prefix.parent / f"{prefix.name}.rows.txt"
    has_rows = rows_path.exists()
    has_mats = any(prefix.parent.glob(f"{prefix.name}.mat.*.npy"))
    has_cols = any(prefix.parent.glob(f"{prefix.name}.cols.*.txt"))
    return has_rows and has_mats and has_cols


def count_feature_chunks(prefix: Path) -> int:
    return len(list(prefix.parent.glob(f"{prefix.name}.cols.*.txt")))


def copy_pre_munged_prefix(source_prefix: Path, dest_prefix: Path) -> int:
    dest_prefix.parent.mkdir(parents=True, exist_ok=True)
    rows_source = source_prefix.parent / f"{source_prefix.name}.rows.txt"
    rows_dest = dest_prefix.parent / f"{dest_prefix.name}.rows.txt"
    shutil.copy2(rows_source, rows_dest)

    chunk_count = 0
    for cols_path in sorted(source_prefix.parent.glob(f"{source_prefix.name}.cols.*.txt")):
        chunk_index = cols_path.stem.split(".")[-1]
        mat_path = source_prefix.parent / f"{source_prefix.name}.mat.{chunk_index}.npy"
        if not mat_path.exists():
            raise FileNotFoundError(f"Missing matrix chunk for feature columns file: {cols_path}")
        shutil.copy2(cols_path, dest_prefix.parent / f"{dest_prefix.name}.cols.{chunk_index}.txt")
        shutil.copy2(mat_path, dest_prefix.parent / f"{dest_prefix.name}.mat.{chunk_index}.npy")
        chunk_count += 1
    return chunk_count
