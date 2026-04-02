from __future__ import annotations

from pathlib import Path

import yaml

from trait2gene.resources.schemas import ResolvedManifest


def write_resolved_manifest(path: Path, manifest: ResolvedManifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(manifest.model_dump(mode="python"), sort_keys=False),
        encoding="utf-8",
    )
