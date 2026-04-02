from __future__ import annotations

import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trait2gene.version import __version__


def software_versions() -> dict[str, str]:
    return {
        "trait2gene": __version__,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }


def timestamp_utc() -> str:
    return datetime.now(UTC).isoformat()


def write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
