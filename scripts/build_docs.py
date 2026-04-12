from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source_dir = root / "docs" / "source"
    build_dir = root / "docs" / "build" / "html"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "html", str(source_dir), str(build_dir)],
        check=True,
    )


if __name__ == "__main__":
    main()

