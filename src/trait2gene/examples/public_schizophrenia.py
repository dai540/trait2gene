from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def build_public_schizophrenia_config(root: Path) -> dict[str, Any]:
    root = root.resolve()
    real_data = root / "real_data" / "pops_upstream_example"
    real_run = root / "real_runs" / "schizophrenia_public_example"
    return {
        "project": "schizophrenia_public_example",
        "trait": "schizophrenia",
        "mode": "advanced",
        "input": {
            "sumstats": str(real_run / "schizophrenia_gwascatalog_hits.tsv"),
            "genome_build": "GRCh37",
            "ancestry": "EUR",
        },
        "columns": {
            "snp": "SNP",
            "p": "P",
            "n": None,
            "chr": "CHR",
            "bp": "BP",
            "a1": None,
            "a2": None,
        },
        "sample_size": {"mode": "fixed", "value": 65967},
        "resources": {
            "magma_bin": "auto",
            "precomputed_magma_prefix": str(
                real_data / "example" / "data" / "magma_scores" / "PASS_Schizophrenia"
            ),
            "gene_annotation": str(real_data / "example" / "data" / "utils" / "gene_annot_jun10.txt"),
            "raw_feature_dir": str(real_data / "example" / "data" / "features_raw"),
            "control_features_path": str(
                real_data / "example" / "data" / "utils" / "features_jul17_control.txt"
            ),
            "feature_bundle": "default_full_v1",
        },
        "analysis": {
            "feature_prep": {"nan_policy": "raise", "max_cols": 500},
            "pops": {
                "method": "ridge",
                "use_magma_covariates": True,
                "use_magma_error_cov": True,
                "remove_hla": True,
                "feature_selection_p_cutoff": 0.05,
                "random_seed": 42,
                "verbose": False,
            },
            "prioritization": {
                "mode": "locus_file",
                "locus_file": str(real_run / "schizophrenia_magma_top_loci.tsv"),
            },
        },
        "output": {
            "outdir": str(real_run / "results"),
            "write_html_report": True,
            "write_json_summary": True,
        },
    }


def write_public_schizophrenia_config(root: Path, config_path: Path | None = None) -> Path:
    root = root.resolve()
    if config_path is None:
        config_path = root / "real_runs" / "schizophrenia_public_example" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config = build_public_schizophrenia_config(root)
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return config_path


def compute_consistency_summary(ours_preds_path: Path, upstream_preds_path: Path) -> dict[str, Any]:
    ours = pd.read_csv(ours_preds_path, sep="\t")
    upstream = pd.read_csv(upstream_preds_path, sep="\t")
    merged = ours.merge(upstream[["ENSGID", "PoPS_Score"]], on="ENSGID", suffixes=("_ours", "_upstream"))
    diff = merged["PoPS_Score_ours"] - merged["PoPS_Score_upstream"]
    return {
        "n_genes_compared": int(len(merged)),
        "pearson_r": float(merged["PoPS_Score_ours"].corr(merged["PoPS_Score_upstream"])),
        "max_abs_diff": float(diff.abs().max()),
        "mean_abs_diff": float(diff.abs().mean()),
    }


def compute_result_snapshot(results_dir: Path) -> dict[str, Any]:
    prioritized = pd.read_csv(results_dir / "tables" / "prioritized_genes.tsv", sep="\t")
    all_ranked = pd.read_csv(results_dir / "tables" / "all_genes_ranked.tsv", sep="\t")
    top_features = pd.read_csv(results_dir / "tables" / "top_features.tsv", sep="\t")
    run_metadata = yaml.safe_load((results_dir / "metadata" / "run_metadata.json").read_text(encoding="utf-8"))
    return {
        "counts": {
            "prioritized_genes": int(len(prioritized)),
            "all_ranked_genes": int(len(all_ranked)),
            "top_features": int(len(top_features)),
        },
        "top_prioritized_genes": prioritized.loc[:, ["locus_id", "gene_symbol"]].to_dict(orient="records"),
        "top_feature_names": top_features["feature"].head(10).tolist(),
        "stage_durations_seconds": {
            row["stage"]: row["duration_seconds"] for row in run_metadata["stages"]
        },
    }
