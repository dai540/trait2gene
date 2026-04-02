from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from trait2gene.config.loader import load_config
from trait2gene.engine.logging import console
from trait2gene.engine.provenance import timestamp_utc, write_json
from trait2gene.io.outputs import ensure_output_layout
from trait2gene.report.html import render_report
from trait2gene.report.tables import top_features_frame
from trait2gene.resources.resolver import resolve_resources


def _find_optional_output(base_dir: Path, suffix: str, trait: str) -> Path | None:
    direct = base_dir / f"{trait}{suffix}"
    if direct.exists():
        return direct
    matches = sorted(base_dir.glob(f"*{suffix}"))
    return matches[0] if matches else None


def run_report(config_path: Path) -> dict[str, object]:
    config = load_config(config_path)
    layout = ensure_output_layout(config.output.outdir)
    manifest = resolve_resources(config)

    prioritized_path = layout["tables"] / "prioritized_genes.tsv"
    all_ranked_path = layout["tables"] / "all_genes_ranked.tsv"
    coefs_path = _find_optional_output(layout["pops"], ".coefs", config.trait)

    prioritized_count = 0
    all_ranked_count = 0
    if prioritized_path.exists():
        prioritized_count = len(pd.read_csv(prioritized_path, sep="\t"))
    if all_ranked_path.exists():
        all_ranked_count = len(pd.read_csv(all_ranked_path, sep="\t"))

    top_features = top_features_frame(coefs_path) if coefs_path else pd.DataFrame()
    top_features_path = layout["tables"] / "top_features.tsv"
    if not top_features.empty:
        top_features.to_csv(top_features_path, sep="\t", index=False)

    summary = {
        "generated_at": timestamp_utc(),
        "project": config.project,
        "trait": config.trait,
        "mode": config.mode,
        "counts": {
            "prioritized_genes": prioritized_count,
            "all_ranked_genes": all_ranked_count,
            "top_features": int(len(top_features)),
        },
        "outputs": {
            "prioritized_genes": str(prioritized_path),
            "all_genes_ranked": str(all_ranked_path),
            "top_features": str(top_features_path) if top_features_path.exists() else None,
        },
        "resources": manifest.model_dump(mode="python"),
    }

    if config.output.write_json_summary:
        write_json(layout["reports"] / "summary.json", summary)
    if config.output.write_html_report:
        html = render_report(summary)
        (layout["reports"] / "report.html").write_text(html, encoding="utf-8")
        template_dir = Path(__file__).resolve().parents[1] / "report" / "templates"
        shutil.copy2(template_dir / "styles.css", layout["reports"] / "styles.css")

    console.print(f"[green]Report assets updated[/green] under {layout['reports']}")
    return summary
