from pathlib import Path

import pandas as pd

from trait2gene.io.outputs import ensure_output_layout
from trait2gene.workflows.prioritize_stage import run_prioritize


def test_prioritize_uses_preds_and_gene_windows(tmp_path: Path) -> None:
    fixtures = Path(__file__).parent / "fixtures"
    sumstats_path = (fixtures / "sumstats.tsv").resolve()
    gene_annot_path = (fixtures / "gene_annot.tsv").resolve()
    outdir = tmp_path / "results" / "bmi_demo"
    ensure_output_layout(outdir)

    preds = pd.DataFrame(
        {
            "ENSGID": ["ENSG0001", "ENSG0002", "ENSG0003"],
            "score": [0.1, 0.9, 0.5],
        }
    )
    preds.to_csv(outdir / "work" / "pops" / "bmi.preds", sep="\t", index=False)

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "project: bmi_demo",
                "trait: bmi",
                "input:",
                f"  sumstats: {sumstats_path}",
                "  genome_build: GRCh37",
                "  ancestry: EAS",
                "resources:",
                "  magma_bin: auto",
                "  reference_panel: auto",
                "  gene_locations: auto",
                f"  gene_annotation: {gene_annot_path}",
                "  feature_bundle: default_full_v1",
                "analysis:",
                "  prioritization:",
                "    mode: lead_snp_window",
                "    window_bp: 500000",
                "output:",
                f"  outdir: {outdir}",
            ]
        ),
        encoding="utf-8",
    )

    prioritized_path = run_prioritize(config_path)
    prioritized = pd.read_csv(prioritized_path, sep="\t")

    assert set(prioritized["gene_symbol"]) == {"GENE2", "GENE3"}
