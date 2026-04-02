from __future__ import annotations

import pandas as pd

from trait2gene.domain.genes import detect_column


def normalize_preds(frame: pd.DataFrame) -> pd.DataFrame:
    gene_id = detect_column(frame.columns, ["ENSGID", "gene_id", "Gene", "GENE", "ensgid"])
    score = detect_column(
        frame.columns,
        ["PoPS_Score", "pops_score", "score", "prediction", "pred", "yhat", "PRED"],
    )
    return pd.DataFrame(
        {
            "gene_id": frame[gene_id].astype(str),
            "pops_score": pd.to_numeric(frame[score], errors="coerce"),
        }
    ).dropna(subset=["pops_score"])


def rank_genes(locus_gene_frame: pd.DataFrame, preds_frame: pd.DataFrame) -> pd.DataFrame:
    merged = locus_gene_frame.merge(preds_frame, on="gene_id", how="left")
    merged["pops_score"] = merged["pops_score"].fillna(float("-inf"))
    ranked = merged.sort_values(
        by=["locus_id", "pops_score", "distance_to_lead_bp"],
        ascending=[True, False, True],
    ).copy()
    ranked["rank_within_locus"] = ranked.groupby("locus_id").cumcount() + 1
    return ranked
