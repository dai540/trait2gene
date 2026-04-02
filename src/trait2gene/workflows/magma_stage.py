from __future__ import annotations

import shutil
from pathlib import Path

from trait2gene.config.defaults import MAGMA_GENE_OUTPUT_SUFFIXES
from trait2gene.config.loader import load_config
from trait2gene.engine.logging import console
from trait2gene.engine.provenance import write_json
from trait2gene.engine.shell import resolve_executable_command, run_command
from trait2gene.io.magma import build_magma_plan
from trait2gene.io.outputs import ensure_output_layout
from trait2gene.io.sumstats import normalize_sumstats
from trait2gene.resources.resolver import resolve_resources


def _copy_magma_outputs(source_prefix: str | Path, destination_prefix: Path) -> None:
    source_path = Path(source_prefix)
    destination_prefix.parent.mkdir(parents=True, exist_ok=True)
    for suffix in MAGMA_GENE_OUTPUT_SUFFIXES:
        shutil.copy2(
            source_path.parent / f"{source_path.name}{suffix}",
            destination_prefix.parent / f"{destination_prefix.name}{suffix}",
        )


def _write_command_logs(metadata_dir: Path, name: str, stdout: str, stderr: str) -> None:
    (metadata_dir / f"{name}.stdout.log").write_text(stdout or "", encoding="utf-8")
    (metadata_dir / f"{name}.stderr.log").write_text(stderr or "", encoding="utf-8")


def run_magma(config_path: Path) -> dict[str, object]:
    config = load_config(config_path)
    layout = ensure_output_layout(config.output.outdir)
    manifest = resolve_resources(config)
    normalized = normalize_sumstats(config, layout["normalized"])
    magma_out_prefix = layout["magma"] / config.trait

    if manifest.magma.precomputed_prefix is not None and all(
        Path(f"{manifest.magma.precomputed_prefix}{suffix}").exists() for suffix in MAGMA_GENE_OUTPUT_SUFFIXES
    ):
        _copy_magma_outputs(manifest.magma.precomputed_prefix, magma_out_prefix)
        payload = {
            "mode": "copy_precomputed",
            "source_prefix": manifest.magma.precomputed_prefix,
            "out_prefix": str(magma_out_prefix),
            "normalized_sumstats": str(normalized.sumstats_path),
        }
        write_json(layout["metadata"] / "magma_plan.json", payload)
        console.print(f"[green]Copied precomputed MAGMA outputs[/green] to {magma_out_prefix}")
        return payload

    if manifest.magma.binary == "auto":
        raise RuntimeError("MAGMA binary is unresolved. Set resources.magma_bin or add magma to PATH.")
    if manifest.reference.status != "resolved":
        raise RuntimeError("Reference panel prefix is unresolved. Set resources.reference_panel.")
    if manifest.gene_locations.status != "resolved":
        raise RuntimeError("Gene locations file is unresolved. Set resources.gene_locations.")

    plan = build_magma_plan(config, manifest, normalized, layout["magma"])
    command_payload = {
        "annotate": resolve_executable_command(plan.annotate[0], *plan.annotate[1:]),
        "gene": resolve_executable_command(plan.gene[0], *plan.gene[1:]),
        "normalized_sumstats": str(normalized.sumstats_path),
        "snploc": str(normalized.snploc_path) if normalized.snploc_path else None,
    }
    write_json(layout["metadata"] / "magma_plan.json", command_payload)

    annotate_result = run_command(command_payload["annotate"])
    _write_command_logs(
        layout["metadata"],
        "magma_annotate",
        annotate_result.stdout,
        annotate_result.stderr,
    )
    if not Path(f"{plan.annotate_out_prefix}.genes.annot").exists():
        raise RuntimeError("MAGMA annotation stage completed without writing .genes.annot output.")

    gene_result = run_command(command_payload["gene"])
    _write_command_logs(
        layout["metadata"],
        "magma_gene",
        gene_result.stdout,
        gene_result.stderr,
    )
    for suffix in MAGMA_GENE_OUTPUT_SUFFIXES:
        if not Path(f"{plan.gene_out_prefix}{suffix}").exists():
            raise RuntimeError(f"MAGMA did not produce expected output: {plan.gene_out_prefix}{suffix}")

    console.print(f"[green]MAGMA outputs written[/green] to {magma_out_prefix}")
    return {
        "mode": "execute",
        "out_prefix": str(magma_out_prefix),
        "normalized_sumstats": str(normalized.sumstats_path),
    }
