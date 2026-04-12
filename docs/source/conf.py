from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trait2gene.version import __version__  # noqa: E402

project = "trait2gene"
author = "Dai"
copyright = "2026, Dai"
version = __version__
release = __version__

extensions = ["myst_parser"]
templates_path: list[str] = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix = {
    ".md": "markdown",
}

html_theme = "furo"
html_title = f"{project} {version}"
html_baseurl = "https://dai540.github.io/trait2gene/"
myst_heading_anchors = 3
