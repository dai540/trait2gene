from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from trait2gene.examples.public_schizophrenia import (
    compute_consistency_summary,
    compute_result_snapshot,
)

ROOT = Path(__file__).resolve().parents[1]
REAL_DATA = ROOT / "real_data" / "pops_upstream_example"
REAL_RUN = ROOT / "real_runs" / "schizophrenia_public_example"
CONFIG_PATH = REAL_RUN / "config.yaml"


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "prepare_public_schizophrenia_example.py")], check=True)
    subprocess.run(["trait2gene", "run", str(CONFIG_PATH)], check=True)

    results_dir = REAL_RUN / "results"
    verification = compute_consistency_summary(
        results_dir / "work" / "pops" / "schizophrenia.preds",
        REAL_DATA / "example" / "out" / "PASS_Schizophrenia.preds",
    )
    snapshot = compute_result_snapshot(results_dir)

    (REAL_RUN / "verification_summary.json").write_text(
        json.dumps(verification, indent=2),
        encoding="utf-8",
    )
    (REAL_RUN / "result_snapshot.json").write_text(
        json.dumps(snapshot, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"verification": verification, "snapshot": snapshot}, indent=2))


if __name__ == "__main__":
    main()
