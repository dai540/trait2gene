from __future__ import annotations

from pathlib import Path

from trait2gene.config.defaults import DEFAULT_FEATURE_PREFIX_BASENAME
from trait2gene.config.loader import load_config
from trait2gene.engine.logging import console
from trait2gene.engine.provenance import write_json
from trait2gene.engine.shell import resolve_executable_command, run_command
from trait2gene.io.features import (
    copy_pre_munged_prefix,
    count_feature_chunks,
    is_pre_munged_prefix,
)
from trait2gene.io.outputs import ensure_output_layout
from trait2gene.resources.resolver import resolve_resources


def _resolved_gene_annotation_path(config, manifest) -> Path:
    candidate = (
        config.resources.gene_annotation
        if config.resources.gene_annotation != "auto"
        else manifest.gene_annotation.path
    )
    path = Path(candidate)
    if not path.exists():
        raise RuntimeError("Gene annotation file is unresolved. Set resources.gene_annotation.")
    return path


def run_feature_prep(config_path: Path) -> dict[str, str | int]:
    config = load_config(config_path)
    layout = ensure_output_layout(config.output.outdir)
    manifest = resolve_resources(config)
    destination_prefix = layout["features"] / DEFAULT_FEATURE_PREFIX_BASENAME

    if manifest.features.format == "pre_munged" and manifest.features.status == "resolved":
        source_prefix = Path(manifest.features.prefix)
        if source_prefix.resolve() != destination_prefix.resolve():
            chunk_count = copy_pre_munged_prefix(source_prefix, destination_prefix)
        else:
            chunk_count = count_feature_chunks(destination_prefix)
        payload = {
            "mode": "use_pre_munged_bundle",
            "source_prefix": manifest.features.prefix,
            "prepared_prefix": str(destination_prefix),
            "num_feature_chunks": chunk_count,
        }
        write_json(layout["metadata"] / "feature_plan.json", payload)
        console.print(f"[green]Using pre-munged feature bundle[/green] {manifest.features.bundle}")
        return payload

    if manifest.features.format == "raw" and manifest.features.status == "resolved":
        vendor_script = Path(__file__).resolve().parents[1] / "vendor" / "pops_upstream" / "munge_feature_directory.py"
        command = resolve_executable_command(
            vendor_script,
            "--gene_annot_path",
            str(_resolved_gene_annotation_path(config, manifest)),
            "--feature_dir",
            str(Path(manifest.features.raw_dir or "")),
            "--nan_policy",
            config.analysis.feature_prep.nan_policy,
            "--save_prefix",
            str(destination_prefix),
            "--max_cols",
            str(config.analysis.feature_prep.max_cols),
        )
        write_json(layout["metadata"] / "feature_plan.json", {"command": command, "prepared_prefix": str(destination_prefix)})
        result = run_command(command)
        (layout["metadata"] / "feature_prep.stdout.log").write_text(result.stdout or "", encoding="utf-8")
        (layout["metadata"] / "feature_prep.stderr.log").write_text(result.stderr or "", encoding="utf-8")
        if not is_pre_munged_prefix(destination_prefix):
            raise RuntimeError("Feature munging completed without producing a valid pre-munged feature prefix.")
        payload = {
            "mode": "munge_raw_features",
            "raw_feature_dir": manifest.features.raw_dir,
            "prepared_prefix": str(destination_prefix),
            "num_feature_chunks": count_feature_chunks(destination_prefix),
        }
        write_json(layout["metadata"] / "feature_plan.json", payload)
        console.print(f"[green]Prepared munged features[/green] under {destination_prefix.parent}")
        return payload

    raise RuntimeError("No usable feature source was resolved. Provide a pre-munged prefix, raw feature directory, or bundle.")
