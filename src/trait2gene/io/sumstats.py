from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from trait2gene.config.models import AppConfig


def read_sumstats_header(path: Path) -> list[str]:
    frame = pd.read_csv(path, sep=None, engine="python", nrows=0)
    return [str(column) for column in frame.columns]


def read_sumstats(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=None, engine="python")


@dataclass(frozen=True)
class NormalizedSumstats:
    sumstats_path: Path
    snploc_path: Path | None
    row_count: int
    columns: list[str]


def required_columns(config: AppConfig) -> list[str]:
    columns: list[str] = [config.columns.snp, config.columns.p]
    if config.sample_size.mode == "column":
        columns.append(str(config.sample_size.value))
    if config.analysis.prioritization.mode == "lead_snp_window":
        for candidate in (config.columns.chr, config.columns.bp):
            if candidate:
                columns.append(candidate)
    return list(dict.fromkeys(columns))


def missing_columns(header: Iterable[str], config: AppConfig) -> list[str]:
    header_set = set(header)
    return [column for column in required_columns(config) if column not in header_set]


def normalize_sumstats(config: AppConfig, output_dir: Path) -> NormalizedSumstats:
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = read_sumstats(config.input.sumstats)

    rename_map = {
        config.columns.snp: "SNP",
        config.columns.p: "P",
    }
    if config.sample_size.mode == "column":
        rename_map[str(config.sample_size.value)] = "N"
    for original, target in (
        (config.columns.chr, "CHR"),
        (config.columns.bp, "BP"),
        (config.columns.a1, "A1"),
        (config.columns.a2, "A2"),
    ):
        if original:
            rename_map[original] = target

    subset = frame.loc[:, list(dict.fromkeys(rename_map.keys()))].rename(columns=rename_map).copy()
    subset["SNP"] = subset["SNP"].astype(str)
    subset["P"] = pd.to_numeric(subset["P"], errors="coerce")
    subset = subset.dropna(subset=["SNP", "P"]).copy()

    if "N" in subset.columns:
        subset["N"] = pd.to_numeric(subset["N"], errors="coerce")
    if "CHR" in subset.columns:
        subset["CHR"] = subset["CHR"].astype(str).str.removeprefix("chr").str.removeprefix("CHR")
    if "BP" in subset.columns:
        subset["BP"] = pd.to_numeric(subset["BP"], errors="coerce")

    sumstats_path = output_dir / f"{config.trait}.sumstats.tsv"
    subset.to_csv(sumstats_path, sep="\t", index=False)

    snploc_path: Path | None = None
    if {"SNP", "CHR", "BP"}.issubset(subset.columns):
        snploc_path = output_dir / f"{config.trait}.snploc.tsv"
        subset.loc[:, ["SNP", "CHR", "BP"]].dropna().to_csv(snploc_path, sep="\t", index=False)

    return NormalizedSumstats(
        sumstats_path=sumstats_path,
        snploc_path=snploc_path,
        row_count=int(len(subset)),
        columns=[str(column) for column in subset.columns],
    )
