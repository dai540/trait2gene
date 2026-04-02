from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np

from trait2gene.workflows import pops_stage


def _write_feature_prefix(prefix: Path) -> None:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    (prefix.parent / f"{prefix.name}.rows.txt").write_text("ENSG0001\nENSG0002\n", encoding="utf-8")
    (prefix.parent / f"{prefix.name}.cols.0.txt").write_text("expr_a\npath_c\n", encoding="utf-8")
    np.save(prefix.parent / f"{prefix.name}.mat.0.npy", np.array([[0.1, 1.0], [0.8, 0.0]]))


def _write_magma_prefix(prefix: Path) -> None:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    (prefix.parent / f"{prefix.name}.genes.out").write_text(
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
    (prefix.parent / f"{prefix.name}.genes.raw").write_text(
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


def test_run_pops_retries_after_subprocess_failure(tmp_path: Path, monkeypatch) -> None:
    outdir = tmp_path / "results" / "demo"
    feature_prefix = outdir / "work" / "features" / "pops_features"
    magma_prefix = outdir / "work" / "magma" / "bmi"
    gene_annot_path = tmp_path / "gene_annot.tsv"
    config_path = tmp_path / "config.yaml"

    _write_feature_prefix(feature_prefix)
    _write_magma_prefix(magma_prefix)
    gene_annot_path.write_text(
        "\n".join(
            [
                "ENSGID\tNAME\tCHR\tSTART\tEND\tTSS",
                "ENSG0001\tG1\t1\t900000\t950000\t925000",
                "ENSG0002\tG2\t2\t1900000\t1950000\t1925000",
                "",
            ]
        ),
        encoding="utf-8",
    )
    config_path.write_text(
        "\n".join(
            [
                "project: demo",
                "trait: bmi",
                "input:",
                f"  sumstats: {tmp_path / 'sumstats.tsv'}",
                "  genome_build: GRCh37",
                "  ancestry: EAS",
                "resources:",
                f"  gene_annotation: {gene_annot_path}",
                "analysis:",
                "  pops:",
                "    method: ridge",
                "output:",
                f"  outdir: {outdir}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "sumstats.tsv").write_text("SNP\tP\tN\tCHR\tBP\tA1\tA2\n", encoding="utf-8")

    calls = {"count": 0}

    def fake_run_command(command, cwd=None, capture_output=True, check=True):
        calls["count"] += 1
        out_prefix = Path(command[command.index("--out_prefix") + 1])
        if calls["count"] == 1:
            raise subprocess.CalledProcessError(
                1,
                command,
                output="first stdout",
                stderr="first stderr",
            )
        for suffix, contents in {
            ".preds": "ENSGID\tPoPS_Score\nENSG0001\t1.0\n",
            ".coefs": "parameter\tbeta\nMETHOD\tRidgeCV\n",
            ".marginals": "feature\tbeta\tse\tpval\tr2\tselected\nexpr_a\t0.1\t0.1\t0.01\t0.5\tTrue\n",
        }.items():
            Path(f"{out_prefix}{suffix}").write_text(contents, encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="second stdout", stderr="")

    monkeypatch.setattr(pops_stage, "run_command", fake_run_command)

    payload = pops_stage.run_pops(config_path)

    assert calls["count"] == 2
    assert payload["out_prefix"] == str(outdir / "work" / "pops" / "bmi")
    assert (outdir / "metadata" / "pops.attempt-1.stderr.log").read_text(encoding="utf-8") == "first stderr"
    assert (outdir / "metadata" / "pops.stdout.log").read_text(encoding="utf-8") == "second stdout"
