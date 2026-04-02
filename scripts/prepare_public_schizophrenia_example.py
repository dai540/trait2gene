from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

from trait2gene.examples.public_schizophrenia import write_public_schizophrenia_config


ROOT = Path(__file__).resolve().parents[1]
REAL_DATA = ROOT / "real_data" / "pops_upstream_example"
REAL_RUN = ROOT / "real_runs" / "schizophrenia_public_example"
GWAS_ASSOCIATION_URL = (
    "https://www.ebi.ac.uk/gwas/rest/api/v2/associations"
    "?efo_id=MONDO_0005090&page=0&size=200"
)


def ensure_upstream_example() -> None:
    if REAL_DATA.exists():
        nested_git = REAL_DATA / ".git"
        if nested_git.exists():
            shutil.rmtree(nested_git)
        return
    REAL_DATA.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", "https://github.com/FinucaneLab/pops.git", str(REAL_DATA)],
        check=True,
    )
    nested_git = REAL_DATA / ".git"
    if nested_git.exists():
        shutil.rmtree(nested_git)


def write_real_sumstats() -> Path:
    with urlopen(GWAS_ASSOCIATION_URL, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    items = payload["_embedded"]["associations"]

    rows: list[dict[str, object]] = []
    for item in items:
        rs_id = None
        if item.get("snp_allele"):
            rs_id = item["snp_allele"][0].get("rs_id")
        if rs_id is None:
            allele = (item.get("snp_effect_allele") or [None])[0]
            if allele and "-" in allele:
                rs_id = allele.split("-", 1)[0]
        location = (item.get("locations") or [None])[0]
        if not rs_id or not location or ":" not in location:
            continue
        chromosome, bp = location.split(":", 1)
        try:
            bp_int = int(bp.replace(",", ""))
        except ValueError:
            continue
        rows.append(
            {
                "SNP": rs_id,
                "P": float(item["p_value"]),
                "CHR": str(chromosome),
                "BP": bp_int,
            }
        )

    df = pd.DataFrame(rows).drop_duplicates(subset=["SNP"]).sort_values("P").reset_index(drop=True)
    output_path = REAL_RUN / "schizophrenia_gwascatalog_hits.tsv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep="\t", index=False)
    return output_path


def write_locus_file() -> Path:
    magma = pd.read_csv(
        REAL_DATA / "example" / "data" / "magma_scores" / "PASS_Schizophrenia.genes.out",
        sep=r"\s+",
    )
    annot = pd.read_csv(
        REAL_DATA / "example" / "data" / "utils" / "gene_annot_jun10.txt",
        sep="\t",
    )
    merged = magma.merge(
        annot[["ENSGID", "NAME", "CHR", "START", "END", "TSS"]],
        left_on="GENE",
        right_on="ENSGID",
        how="left",
    )
    merged = merged[
        ~(
            (merged["CHR_x"].astype(str) == "6")
            & (merged["START_x"] >= 25_000_000)
            & (merged["STOP"] <= 34_000_000)
        )
    ].copy()
    merged = merged.sort_values("P")

    selected: list[dict[str, object]] = []
    for row in merged.itertuples(index=False):
        chrom = str(row.CHR_x)
        start = max(0, int(row.START_x) - 500_000)
        end = int(row.STOP) + 500_000
        overlaps = any(
            locus["CHR"] == chrom and not (end < locus["START"] or start > locus["END"])
            for locus in selected
        )
        if overlaps:
            continue
        selected.append(
            {
                "locus_id": f"magma_top_{len(selected) + 1:02d}",
                "CHR": chrom,
                "START": start,
                "END": end,
                "lead_bp": int(row.TSS),
                "lead_p": float(row.P),
                "gene_id": row.GENE,
                "gene_symbol": row.NAME,
            }
        )
        if len(selected) == 8:
            break

    output_path = REAL_RUN / "schizophrenia_magma_top_loci.tsv"
    pd.DataFrame(selected).to_csv(output_path, sep="\t", index=False)
    return output_path


def main() -> None:
    ensure_upstream_example()
    REAL_RUN.mkdir(parents=True, exist_ok=True)
    sumstats_path = write_real_sumstats()
    locus_path = write_locus_file()
    config_path = write_public_schizophrenia_config(ROOT, REAL_RUN / "config.yaml")
    summary = {
        "upstream_example": str(REAL_DATA),
        "gwascatalog_association_url": GWAS_ASSOCIATION_URL,
        "sumstats_path": str(sumstats_path),
        "locus_path": str(locus_path),
        "config_path": str(config_path),
    }
    (REAL_RUN / "download_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
