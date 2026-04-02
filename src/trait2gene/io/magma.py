from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from trait2gene.config.models import AppConfig
from trait2gene.io.sumstats import NormalizedSumstats
from trait2gene.resources.schemas import ResolvedManifest


@dataclass(frozen=True)
class MagmaExecutionPlan:
    annotate: list[str]
    gene: list[str]
    annotate_out_prefix: Path
    gene_out_prefix: Path


def build_magma_plan(
    config: AppConfig,
    manifest: ResolvedManifest,
    normalized: NormalizedSumstats,
    outdir: Path,
) -> MagmaExecutionPlan:
    annot_out = outdir / "annot"
    genes_out = outdir / config.trait
    n_value = config.sample_size.value
    pval_spec = f"N={n_value}" if config.sample_size.mode == "fixed" else "ncol=N"
    snp_loc = (
        Path(f"{manifest.reference.path_prefix}.bim")
        if config.analysis.magma.annotation_snp_loc_source == "reference_bim"
        else normalized.snploc_path
    )
    if snp_loc is None:
        raise ValueError(
            "No SNP-location source was available for MAGMA annotation. "
            "Provide CHR/BP columns or use a resolved reference panel prefix."
        )

    return MagmaExecutionPlan(
        annotate=[
            manifest.magma.binary,
            "--annotate",
            "--snp-loc",
            str(snp_loc),
            "--gene-loc",
            manifest.gene_locations.path,
            "--out",
            str(annot_out),
        ],
        gene=[
            manifest.magma.binary,
            "--bfile",
            manifest.reference.path_prefix,
            "--pval",
            str(normalized.sumstats_path),
            pval_spec,
            "use=SNP,P",
            "--gene-model",
            config.analysis.magma.model,
            "--gene-annot",
            f"{annot_out}.genes.annot",
            "--out",
            str(genes_out),
        ],
        annotate_out_prefix=annot_out,
        gene_out_prefix=genes_out,
    )
