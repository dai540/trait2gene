from __future__ import annotations

from pathlib import Path

from trait2gene.config.defaults import OUTPUT_LAYOUT


def ensure_output_layout(outdir: Path) -> dict[str, Path]:
    outdir = outdir.expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    resolved = {name: outdir / rel_path for name, rel_path in OUTPUT_LAYOUT.items()}
    for path in resolved.values():
        path.mkdir(parents=True, exist_ok=True)
    return resolved
