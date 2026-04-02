from __future__ import annotations

from pathlib import Path

from trait2gene.vendor.pops_upstream.pops import read_gene_annot_df, read_magma


def test_read_gene_annot_df_accepts_whitespace_separated_input(tmp_path: Path) -> None:
    gene_annot_path = tmp_path / "gene_annot.txt"
    gene_annot_path.write_text(
        "\n".join(
            [
                "ENSGID NAME CHR START END TSS",
                "ENSG0001 G1 1 900000 950000 925000",
                "ENSG0002 G2 2 1900000 1950000 1925000",
                "",
            ]
        ),
        encoding="utf-8",
    )

    gene_annot_df = read_gene_annot_df(str(gene_annot_path))

    assert list(gene_annot_df.index) == ["ENSG0001", "ENSG0002"]
    assert list(gene_annot_df["CHR"]) == ["1", "2"]


def test_read_magma_accepts_whitespace_separated_output(tmp_path: Path) -> None:
    magma_prefix = tmp_path / "toy"
    (tmp_path / "toy.genes.out").write_text(
        "\n".join(
            [
                "GENE CHR START STOP NSNPS NPARAM N ZSTAT P",
                "ENSG0001 1 900000 950000 20 2 100000 3.0 0.001",
                "ENSG0002 2 1900000 1950000 22 2 100000 1.9 0.003",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "toy.genes.raw").write_text(
        "\n".join(
            [
                "# VERSION = 108",
                "# COVAR = NSAMP MAC",
                "ENSG0001 1 900000 950000 20 2 100000 120.9 3.0",
                "ENSG0002 2 1900000 1950000 22 2 100000 121.9 1.9",
                "",
            ]
        ),
        encoding="utf-8",
    )

    y, covariates, error_cov, y_ids = read_magma(str(magma_prefix), True, True)

    assert list(y_ids) == ["ENSG0001", "ENSG0002"]
    assert list(y) == [3.0, 1.9]
    assert covariates is not None
    assert error_cov is not None
