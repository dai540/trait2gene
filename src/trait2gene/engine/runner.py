from __future__ import annotations

import time
from pathlib import Path

from trait2gene.config.loader import load_config
from trait2gene.engine.plan import planned_stage_functions
from trait2gene.engine.provenance import timestamp_utc, write_json
from trait2gene.io.outputs import ensure_output_layout


def run_pipeline(config_path: Path) -> None:
    config = load_config(config_path)
    layout = ensure_output_layout(config.output.outdir)
    stages = planned_stage_functions(config)
    records: list[dict[str, object]] = []
    run_started_at = timestamp_utc()
    for name, stage_fn in stages:
        started = time.perf_counter()
        try:
            stage_fn(config_path)
        except Exception as exc:
            records.append(
                {
                    "stage": name,
                    "status": "error",
                    "duration_seconds": round(time.perf_counter() - started, 4),
                    "error": str(exc),
                }
            )
            write_json(
                layout["metadata"] / "run_metadata.json",
                {
                    "config_path": str(config_path),
                    "run_started_at": run_started_at,
                    "run_finished_at": timestamp_utc(),
                    "status": "error",
                    "stages": records,
                },
            )
            raise
        else:
            records.append(
                {
                    "stage": name,
                    "status": "ok",
                    "duration_seconds": round(time.perf_counter() - started, 4),
                }
            )
    write_json(
        layout["metadata"] / "run_metadata.json",
        {
            "config_path": str(config_path),
            "run_started_at": run_started_at,
            "run_finished_at": timestamp_utc(),
            "status": "ok",
            "stages": records,
        },
    )
