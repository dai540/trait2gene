from __future__ import annotations

from pathlib import Path

import pandas as pd

from trait2gene.config.loader import load_config
from trait2gene.domain.loci import compute_lead_windows, load_locus_file
from trait2gene.domain.ranking import normalize_preds, rank_genes
from trait2gene.engine.logging import console
from trait2gene.io.annotations import load_gene_annotation
from trait2gene.io.outputs import ensure_output_layout
from trait2gene.io.sumstats import read_sumstats
from trait2gene.resources.resolver import resolve_resources


def _resolve_gene_annotation_path(config, manifest) -> Path:
    candidate = (
        config.resources.gene_annotation
        if config.resources.gene_annotation != "auto"
        else manifest.gene_annotation.path
    )
    path = Path(candidate)
    if not path.exists():
        raise RuntimeError(
            "Gene annotation path is unresolved. Set resources.gene_annotation to a local TSV file "
            "before running prioritize."
        )
    return path


def _find_preds_path(pops_dir: Path, trait: str) -> Path:
    direct = pops_dir / f"{trait}.preds"
    if direct.exists():
        return direct
    matches = sorted(pops_dir.glob("*.preds"))
    if not matches:
        raise RuntimeError("No PoPS prediction file was found under work/pops.")
    return matches[0]


def _distance_to_window(row: pd.Series, lead_bp: int) -> int:
    return min(abs(int(row["start"]) - lead_bp), abs(int(row["end"]) - lead_bp))


def run_prioritize(config_path: Path) -> Path:
    config = load_config(config_path)
    layout = ensure_output_layout(config.output.outdir)
    manifest = resolve_resources(config)

    if config.analysis.prioritization.mode == "lead_snp_window":
        if not config.columns.chr or not config.columns.bp:
            raise RuntimeError("columns.chr and columns.bp are required for lead_snp_window mode.")
        sumstats = read_sumstats(config.input.sumstats)
        windows = compute_lead_windows(
            sumstats,
            chromosome_column=config.columns.chr,
            bp_column=config.columns.bp,
            p_column=config.columns.p,
            snp_column=config.columns.snp,
            window_bp=config.analysis.prioritization.window_bp,
        )
    else:
        if config.analysis.prioritization.locus_file is None:
            raise RuntimeError("analysis.prioritization.locus_file is required when mode=locus_file.")
        windows = load_locus_file(config.analysis.prioritization.locus_file)
    if not windows:
        raise RuntimeError("No lead loci could be derived from the provided summary statistics.")

    gene_annotation = load_gene_annotation(_resolve_gene_annotation_path(config, manifest))
    locus_gene_frames: list[pd.DataFrame] = []
    for window in windows:
        overlap = gene_annotation[
            (gene_annotation["chromosome"] == window.chromosome)
            & (gene_annotation["start"] <= window.end)
            & (gene_annotation["end"] >= window.start)
        ].copy()
        if overlap.empty:
            continue
        overlap["locus_id"] = window.locus_id
        overlap["lead_snp"] = window.lead_snp
        overlap["lead_bp"] = window.lead_bp
        overlap["lead_p"] = window.lead_p
        overlap["window_start"] = window.start
        overlap["window_end"] = window.end
        overlap["distance_to_lead_bp"] = overlap.apply(
            _distance_to_window,
            axis=1,
            lead_bp=window.lead_bp if window.lead_bp is not None else int((window.start + window.end) / 2),
        )
        locus_gene_frames.append(overlap)

    if not locus_gene_frames:
        raise RuntimeError("No genes overlapped the derived lead-SNP windows.")

    locus_gene_frame = pd.concat(locus_gene_frames, ignore_index=True)
    preds_frame = normalize_preds(pd.read_csv(_find_preds_path(layout["pops"], config.trait), sep=None, engine="python"))
    ranked = rank_genes(locus_gene_frame, preds_frame)
    ranked["is_top_gene"] = ranked["rank_within_locus"] == 1

    all_ranked_path = layout["tables"] / "all_genes_ranked.tsv"
    prioritized_path = layout["tables"] / "prioritized_genes.tsv"
    ranked.to_csv(all_ranked_path, sep="\t", index=False)
    ranked[ranked["is_top_gene"]].to_csv(prioritized_path, sep="\t", index=False)
    pd.DataFrame([window.__dict__ for window in windows]).to_csv(layout["tables"] / "loci.tsv", sep="\t", index=False)
    console.print(f"[green]Wrote prioritized genes[/green] to {prioritized_path}")
    return prioritized_path
