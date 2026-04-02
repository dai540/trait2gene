from pathlib import Path

from typer.testing import CliRunner

from trait2gene.cli import app


def test_validate_command_writes_qc(tmp_path: Path) -> None:
    fixtures = Path(__file__).parent / "fixtures"
    sumstats_path = (fixtures / "sumstats.tsv").resolve()
    outdir = tmp_path / "results" / "bmi_demo"
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
                "output:",
                f"  outdir: {outdir}",
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["validate", str(config_path)])
    assert result.exit_code == 0, result.stdout
    assert (outdir / "qc" / "input_qc.json").exists()
