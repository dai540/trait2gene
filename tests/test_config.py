from pathlib import Path

from trait2gene.config.loader import load_config


def test_load_config_resolves_relative_paths() -> None:
    config_path = Path(__file__).parent / "fixtures" / "minimal_config.yaml"
    config = load_config(config_path)

    assert config.input.sumstats.is_absolute()
    assert config.output.outdir.is_absolute()
    assert config.analysis.pops.method == "ridge"
    assert config.analysis.pops.remove_hla is True
