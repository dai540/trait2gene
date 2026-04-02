from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from trait2gene.engine.runner import run_pipeline


def _write_fake_magma_script(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "",
                "import sys",
                "from pathlib import Path",
                "",
                "",
                "GENES = [",
                "    ('ENSG0001', '1', 900000, 950000, 20, 2, 100000, 3.0, 0.0010, None),",
                "    ('ENSG0002', '1', 1100000, 1150000, 20, 2, 100000, 2.4, 0.0020, 0.10),",
                "    ('ENSG0003', '2', 1900000, 1950000, 22, 2, 100000, 1.9, 0.0030, None),",
                "    ('ENSG0004', '2', 2100000, 2150000, 22, 2, 100000, 1.4, 0.0040, 0.05),",
                "    ('ENSG0005', '3', 3000000, 3050000, 24, 2, 100000, 0.9, 0.0050, None),",
                "    ('ENSG0006', '3', 3200000, 3250000, 24, 2, 100000, 0.6, 0.0060, 0.02),",
                "]",
                "",
                "",
                "def _argument(args: list[str], flag: str) -> str:",
                "    return args[args.index(flag) + 1]",
                "",
                "",
                "def _write_annotate(out_prefix: Path) -> None:",
                "    Path(str(out_prefix) + '.genes.annot').write_text('GENE ANNOT\\n', encoding='utf-8')",
                "",
                "",
                "def _write_gene(out_prefix: Path) -> None:",
                "    genes_out = [",
                "        'GENE CHR START STOP NSNPS NPARAM N ZSTAT P',",
                "    ]",
                "    genes_raw = [",
                "        '# VERSION = 108',",
                "        '# COVAR = NSAMP MAC',",
                "    ]",
                "    for gene, chrom, start, stop, nsnps, nparam, n_value, zstat, pval, corr in GENES:",
                "        genes_out.append(f'{gene} {chrom} {start} {stop} {nsnps} {nparam} {n_value} {zstat} {pval}')",
                "        raw_line = f'{gene} {chrom} {start} {stop} {nsnps} {nparam} {n_value} {120.0 + float(start) / 1000000.0:.3f} {zstat}'",
                "        if corr is not None:",
                "            raw_line += f' {corr}'",
                "        genes_raw.append(raw_line)",
                "    Path(str(out_prefix) + '.genes.out').write_text('\\n'.join(genes_out) + '\\n', encoding='utf-8')",
                "    Path(str(out_prefix) + '.genes.raw').write_text('\\n'.join(genes_raw) + '\\n', encoding='utf-8')",
                "",
                "",
                "def main() -> int:",
                "    args = sys.argv[1:]",
                "    if '--version' in args:",
                "        print('MAGMA v1.10 (fake)')",
                "        return 0",
                "    if '--help' in args:",
                "        print('fake magma help')",
                "        return 0",
                "    out_prefix = Path(_argument(args, '--out'))",
                "    out_prefix.parent.mkdir(parents=True, exist_ok=True)",
                "    if '--annotate' in args:",
                "        _write_annotate(out_prefix)",
                "        return 0",
                "    _write_gene(out_prefix)",
                "    return 0",
                "",
                "",
                "if __name__ == '__main__':",
                "    raise SystemExit(main())",
            ]
        ),
        encoding="utf-8",
    )


def test_run_pipeline_end_to_end_with_fake_magma(tmp_path: Path) -> None:
    raw_feature_dir = tmp_path / "raw_features"
    raw_feature_dir.mkdir()
    gene_annot_path = tmp_path / "gene_annot.tsv"
    gene_loc_path = tmp_path / "gene_loc.tsv"
    sumstats_path = tmp_path / "sumstats.tsv"
    control_features_path = tmp_path / "control_features.txt"
    fake_magma_path = tmp_path / "fake_magma.py"
    ref_prefix = tmp_path / "reference" / "toy_ref"
    ref_prefix.parent.mkdir()

    for suffix in (".bed", ".bim", ".fam"):
        (ref_prefix.parent / f"{ref_prefix.name}{suffix}").write_text("stub\n", encoding="utf-8")

    gene_annot = pd.DataFrame(
        {
            "ENSGID": ["ENSG0001", "ENSG0002", "ENSG0003", "ENSG0004", "ENSG0005", "ENSG0006"],
            "NAME": ["G1", "G2", "G3", "G4", "G5", "G6"],
            "CHR": ["1", "1", "2", "2", "3", "3"],
            "START": [900000, 1100000, 1900000, 2100000, 3000000, 3200000],
            "END": [950000, 1150000, 1950000, 2150000, 3050000, 3250000],
            "TSS": [925000, 1125000, 1925000, 2125000, 3025000, 3225000],
        }
    )
    gene_annot.to_csv(gene_annot_path, sep="\t", index=False)
    gene_annot.to_csv(gene_loc_path, sep="\t", index=False)

    pd.DataFrame(
        {
            "ENSGID": gene_annot["ENSGID"],
            "expr_a": [0.1, 0.8, 0.2, 0.6, 0.3, 0.4],
            "expr_b": [0.9, 0.2, 0.7, 0.3, 0.4, 0.5],
        }
    ).to_csv(raw_feature_dir / "expression.tsv", sep="\t", index=False)
    pd.DataFrame(
        {
            "ENSGID": gene_annot["ENSGID"],
            "path_c": [1.0, 0.0, 0.8, 0.2, 0.6, 0.4],
            "path_d": [0.2, 0.3, 0.5, 0.7, 0.9, 1.1],
        }
    ).to_csv(raw_feature_dir / "pathways.tsv", sep="\t", index=False)

    control_features_path.write_text("expr_a\npath_c\n", encoding="utf-8")
    _write_fake_magma_script(fake_magma_path)

    pd.DataFrame(
        {
            "SNP": ["rs1", "rs2", "rs3"],
            "P": [1.0e-8, 2.0e-7, 5.0e-6],
            "N": [100000, 100000, 100000],
            "CHR": ["1", "2", "3"],
            "BP": [1000000, 2000000, 3100000],
            "A1": ["A", "C", "G"],
            "A2": ["G", "T", "A"],
        }
    ).to_csv(sumstats_path, sep="\t", index=False)

    outdir = tmp_path / "results" / "demo"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "project: demo",
                "trait: bmi",
                "input:",
                f"  sumstats: {sumstats_path}",
                "  genome_build: GRCh37",
                "  ancestry: EAS",
                "resources:",
                f"  magma_bin: {fake_magma_path}",
                f"  reference_panel: {ref_prefix}",
                f"  gene_locations: {gene_loc_path}",
                f"  gene_annotation: {gene_annot_path}",
                f"  raw_feature_dir: {raw_feature_dir}",
                f"  control_features_path: {control_features_path}",
                "  feature_bundle: default_full_v1",
                "analysis:",
                "  feature_prep:",
                "    max_cols: 2",
                "  pops:",
                "    method: ridge",
                "    feature_selection_p_cutoff: 0.05",
                "output:",
                f"  outdir: {outdir}",
            ]
        ),
        encoding="utf-8",
    )

    run_pipeline(config_path)

    assert (outdir / "work" / "magma" / "bmi.genes.out").exists()
    assert (outdir / "work" / "features" / "pops_features.rows.txt").exists()
    assert (outdir / "work" / "pops" / "bmi.preds").exists()
    assert (outdir / "tables" / "prioritized_genes.tsv").exists()
    assert (outdir / "reports" / "report.html").exists()
    assert (outdir / "reports" / "styles.css").exists()

    run_metadata = json.loads((outdir / "metadata" / "run_metadata.json").read_text(encoding="utf-8"))
    assert run_metadata["status"] == "ok"
    assert [stage["stage"] for stage in run_metadata["stages"]] == [
        "validate",
        "prepare",
        "magma",
        "feature_prep",
        "pops",
        "prioritize",
        "report",
    ]
