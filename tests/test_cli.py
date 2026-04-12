from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_init_validate_and_run(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH")
    src_path = str(root / "src")
    env["PYTHONPATH"] = src_path if not pythonpath else os.pathsep.join([src_path, pythonpath])
    config_path = tmp_path / "config.toml"
    subprocess.run(
        [sys.executable, "-m", "trait2gene", "init", str(config_path)],
        check=True,
        env=env,
    )

    inputs = tmp_path / "inputs"
    inputs.mkdir()
    (inputs / "example.tsv").write_text("SNP\tP\nrs1\t0.01\n", encoding="utf-8")

    config_path.write_text(
        config_path.read_text(encoding="utf-8").replace("example_trait", "demo_trait"),
        encoding="utf-8",
    )

    validate = subprocess.run(
        [sys.executable, "-m", "trait2gene", "validate", str(config_path)],
        check=True,
        capture_output=True,
        env=env,
        text=True,
    )
    assert "Validation passed" in validate.stdout

    subprocess.run(
        [sys.executable, "-m", "trait2gene", "run", str(config_path)],
        check=True,
        env=env,
    )

    assert (tmp_path / "results" / "demo_trait" / "metadata" / "run-summary.json").exists()
    assert (tmp_path / "results" / "demo_trait" / "reports" / "summary.md").exists()
