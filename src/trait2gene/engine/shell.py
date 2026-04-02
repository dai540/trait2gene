from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path


def resolve_executable_command(executable: str | Path, *args: str) -> list[str]:
    executable_path = str(executable)
    if executable_path.lower().endswith(".py"):
        return [sys.executable, executable_path, *args]
    return [executable_path, *args]


def run_command(
    command: Sequence[str],
    cwd: Path | None = None,
    capture_output: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        capture_output=capture_output,
    )
