from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from trait2gene.domain.genes import coerce_chromosome, detect_column


@dataclass(frozen=True)
class LocusWindow:
    locus_id: str
    chromosome: str
    lead_snp: str | None
    lead_bp: int | None
    lead_p: float | None
    start: int
    end: int


def compute_lead_windows(
    sumstats: pd.DataFrame,
    *,
    chromosome_column: str,
    bp_column: str,
    p_column: str,
    snp_column: str,
    window_bp: int,
) -> list[LocusWindow]:
    frame = sumstats[[chromosome_column, bp_column, p_column, snp_column]].copy()
    frame[chromosome_column] = frame[chromosome_column].map(coerce_chromosome)
    frame[bp_column] = pd.to_numeric(frame[bp_column], errors="coerce")
    frame[p_column] = pd.to_numeric(frame[p_column], errors="coerce")
    frame = frame.dropna(subset=[chromosome_column, bp_column, p_column]).sort_values(
        by=p_column,
        ascending=True,
    )

    windows: list[LocusWindow] = []
    for _, row in frame.iterrows():
        chromosome = str(row[chromosome_column])
        position = int(row[bp_column])
        overlaps = any(
            existing.chromosome == chromosome and existing.start <= position <= existing.end
            for existing in windows
        )
        if overlaps:
            continue
        locus_number = len(windows) + 1
        windows.append(
            LocusWindow(
                locus_id=f"locus_{locus_number:03d}",
                chromosome=chromosome,
                lead_snp=str(row[snp_column]),
                lead_bp=position,
                lead_p=float(row[p_column]),
                start=max(0, position - window_bp),
                end=position + window_bp,
            )
        )
    return windows


def load_locus_file(path: str | Path) -> list[LocusWindow]:
    frame = pd.read_csv(path, sep=None, engine="python")
    locus_id = detect_column(frame.columns, ["locus_id", "LOCUS", "locus"], required=False)
    chromosome = detect_column(frame.columns, ["CHR", "chr", "chromosome"])
    start = detect_column(frame.columns, ["START", "start", "begin"])
    end = detect_column(frame.columns, ["END", "end", "stop"])
    lead_snp = detect_column(frame.columns, ["lead_snp", "LEAD_SNP", "SNP"], required=False)
    lead_bp = detect_column(frame.columns, ["lead_bp", "LEAD_BP", "BP"], required=False)
    lead_p = detect_column(frame.columns, ["lead_p", "LEAD_P", "P"], required=False)

    windows: list[LocusWindow] = []
    for index, row in frame.iterrows():
        start_value = int(pd.to_numeric(row[start], errors="raise"))
        end_value = int(pd.to_numeric(row[end], errors="raise"))
        chromosome_value = coerce_chromosome(row[chromosome])
        if chromosome_value is None:
            raise ValueError(f"Could not coerce chromosome value in locus row {index + 1}.")
        lead_bp_value = (
            int(pd.to_numeric(row[lead_bp], errors="coerce")) if lead_bp else int((start_value + end_value) / 2)
        )
        lead_p_value = float(pd.to_numeric(row[lead_p], errors="coerce")) if lead_p else None
        windows.append(
            LocusWindow(
                locus_id=str(row[locus_id]) if locus_id else f"locus_{index + 1:03d}",
                chromosome=str(chromosome_value),
                lead_snp=str(row[lead_snp]) if lead_snp else None,
                lead_bp=lead_bp_value,
                lead_p=lead_p_value,
                start=min(start_value, end_value),
                end=max(start_value, end_value),
            )
        )
    return windows
