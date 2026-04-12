from __future__ import annotations

from pathlib import Path

from trait2gene.config import load_config, validate_config


def test_load_config_resolves_relative_paths(tmp_path: Path) -> None:
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    (inputs / "demo.tsv").write_text("SNP\tP\nrs1\t0.01\n", encoding="utf-8")
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "\n".join(
            [
                'project = "demo"',
                'trait = "bmi"',
                "",
                "[input]",
                'sumstats = "inputs/demo.tsv"',
                'genome_build = "GRCh37"',
                'ancestry = "EUR"',
                "",
                "[resources]",
                "",
                "[execution]",
                'mode = "plan"',
                "",
                "[output]",
                'outdir = "results/demo"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.input.sumstats == (inputs / "demo.tsv").resolve()
    assert config.output.outdir == (tmp_path / "results" / "demo").resolve()
    assert validate_config(config) == []


def test_run_mode_requires_resources(tmp_path: Path) -> None:
    sumstats = tmp_path / "demo.tsv"
    sumstats.write_text("SNP\tP\nrs1\t0.01\n", encoding="utf-8")
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "\n".join(
            [
                'project = "demo"',
                'trait = "bmi"',
                "",
                "[input]",
                'sumstats = "demo.tsv"',
                'genome_build = "GRCh37"',
                'ancestry = "EUR"',
                "",
                "[resources]",
                "",
                "[execution]",
                'mode = "run"',
                "",
                "[output]",
                'outdir = "results/demo"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    errors = validate_config(load_config(config_path))

    assert any("resources.gene_annotation" in error for error in errors)
    assert any(
        "resources.magma_bin" in error or "resources.precomputed_magma_prefix" in error
        for error in errors
    )
    assert any(
        "resources.feature_prefix" in error or "resources.raw_feature_dir" in error
        for error in errors
    )
