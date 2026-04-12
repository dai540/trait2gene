from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from trait2gene.config import AppConfig


@dataclass(frozen=True)
class Stage:
    name: str
    summary: str


def build_stage_plan(config: AppConfig) -> list[Stage]:
    magma_summary = (
        "Reuse precomputed MAGMA prefix"
        if config.resources.precomputed_magma_prefix is not None
        else "Expect an external MAGMA binary"
    )
    feature_summary = (
        "Reuse feature prefix"
        if config.resources.feature_prefix is not None
        else "Expect raw feature directory"
    )
    return [
        Stage(name="validate", summary="Check configuration and local paths"),
        Stage(name="prepare", summary="Create compact output directories and metadata"),
        Stage(name="magma", summary=magma_summary),
        Stage(name="feature_prep", summary=feature_summary),
        Stage(name="pops", summary="Reserve a stage for external gene-prioritization execution"),
        Stage(name="prioritize", summary="Reserve a stage for locus-level ranking"),
        Stage(name="report", summary="Write a lightweight Markdown and HTML summary"),
    ]


def _json_default(value: object) -> str:
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Unsupported JSON value: {type(value)!r}")


def materialize_run(config: AppConfig, config_text: str) -> Path:
    outdir = config.output.outdir
    metadata_dir = outdir / "metadata"
    reports_dir = outdir / "reports"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    stage_plan = build_stage_plan(config)
    summary = {
        "project": config.project,
        "trait": config.trait,
        "execution_mode": config.execution.mode,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "stage_count": len(stage_plan),
        "stages": [asdict(stage) for stage in stage_plan],
    }

    (metadata_dir / "config.snapshot.toml").write_text(config_text, encoding="utf-8")
    (metadata_dir / "stage-plan.json").write_text(
        json.dumps(summary["stages"], indent=2),
        encoding="utf-8",
    )
    (metadata_dir / "run-summary.json").write_text(
        json.dumps(summary, indent=2, default=_json_default),
        encoding="utf-8",
    )

    markdown_lines = [
        f"# trait2gene run summary: {config.project}",
        "",
        f"- trait: `{config.trait}`",
        f"- execution mode: `{config.execution.mode}`",
        f"- output directory: `{outdir}`",
        "",
        "## Stage plan",
        "",
    ]
    for stage in stage_plan:
        markdown_lines.append(f"- `{stage.name}`: {stage.summary}")
    (reports_dir / "summary.md").write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")

    if config.execution.write_html:
        html = [
            "<!doctype html>",
            "<html lang='en'>",
            "<head>",
            "  <meta charset='utf-8'>",
            "  <title>trait2gene run summary</title>",
            (
                "  <style>"
                "body{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:760px;"
                "margin:40px auto;padding:0 16px;line-height:1.6;color:#1f2933}"
                "code{background:#eef2f6;padding:2px 6px;border-radius:4px}"
                "</style>"
            ),
            "</head>",
            "<body>",
            f"  <h1>{config.project}</h1>",
            f"  <p><strong>Trait:</strong> <code>{config.trait}</code></p>",
            f"  <p><strong>Execution mode:</strong> <code>{config.execution.mode}</code></p>",
            "  <h2>Stage plan</h2>",
            "  <ul>",
        ]
        for stage in stage_plan:
            html.append(f"    <li><code>{stage.name}</code>: {stage.summary}</li>")
        html.extend(["  </ul>", "</body>", "</html>"])
        (reports_dir / "index.html").write_text("\n".join(html), encoding="utf-8")

    return outdir
