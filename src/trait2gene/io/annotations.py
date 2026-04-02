from __future__ import annotations

from pathlib import Path

import pandas as pd

from trait2gene.domain.genes import coerce_chromosome, detect_column


def load_gene_annotation(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, sep=None, engine="python")
    gene_id = detect_column(frame.columns, ["ENSGID", "gene_id", "ensgid", "GENE_ID"])
    gene_symbol = detect_column(
        frame.columns,
        ["gene_symbol", "symbol", "SYMBOL", "GENE_SYMBOL", "NAME", "name"],
        required=False,
    )
    chromosome = detect_column(frame.columns, ["CHR", "chr", "chromosome", "seqname"])
    start = detect_column(frame.columns, ["START", "start", "TSS", "tss"])
    end = detect_column(frame.columns, ["END", "end", "TES", "tes"], required=False)

    normalized = pd.DataFrame(
        {
            "gene_id": frame[gene_id].astype(str),
            "gene_symbol": frame[gene_symbol].astype(str) if gene_symbol else frame[gene_id].astype(str),
            "chromosome": frame[chromosome].map(coerce_chromosome),
            "start": pd.to_numeric(frame[start], errors="coerce"),
            "end": pd.to_numeric(frame[end], errors="coerce")
            if end
            else pd.to_numeric(frame[start], errors="coerce"),
        }
    )
    normalized = normalized.dropna(subset=["chromosome", "start", "end"]).copy()
    normalized["start"] = normalized["start"].astype(int)
    normalized["end"] = normalized["end"].astype(int)
    return normalized
