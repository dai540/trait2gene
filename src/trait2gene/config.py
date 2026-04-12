from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

ALLOWED_ANCESTRIES = {"EUR", "AFR", "EAS", "SAS", "AMR"}
ALLOWED_BUILDS = {"GRCh37", "GRCh38"}
ALLOWED_EXECUTION_MODES = {"plan", "run"}


class ConfigError(ValueError):
    """Raised when a configuration file is invalid."""


@dataclass(frozen=True)
class InputConfig:
    sumstats: Path
    genome_build: str
    ancestry: str


@dataclass(frozen=True)
class ResourcesConfig:
    magma_bin: Path | None = None
    precomputed_magma_prefix: Path | None = None
    feature_prefix: Path | None = None
    raw_feature_dir: Path | None = None
    gene_annotation: Path | None = None


@dataclass(frozen=True)
class ExecutionConfig:
    mode: str = "plan"
    write_html: bool = True


@dataclass(frozen=True)
class OutputConfig:
    outdir: Path


@dataclass(frozen=True)
class AppConfig:
    project: str
    trait: str
    input: InputConfig
    resources: ResourcesConfig
    execution: ExecutionConfig
    output: OutputConfig


def resolve_path(raw: str | None, *, base_dir: Path) -> Path | None:
    if raw is None or raw == "":
        return None
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return path


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path).expanduser().resolve()
    if not config_path.exists():
        raise ConfigError(f"Config file does not exist: {config_path}")
    with config_path.open("rb") as handle:
        raw = tomllib.load(handle)
    base_dir = config_path.parent

    try:
        project = str(raw["project"]).strip()
        trait = str(raw["trait"]).strip()
        input_raw = raw["input"]
        output_raw = raw["output"]
    except KeyError as exc:
        raise ConfigError(f"Missing required top-level key: {exc.args[0]}") from exc

    resources_raw = raw.get("resources", {})
    execution_raw = raw.get("execution", {})

    return AppConfig(
        project=project,
        trait=trait,
        input=InputConfig(
            sumstats=resolve_path(str(input_raw["sumstats"]), base_dir=base_dir),  # type: ignore[arg-type]
            genome_build=str(input_raw["genome_build"]),
            ancestry=str(input_raw["ancestry"]),
        ),
        resources=ResourcesConfig(
            magma_bin=resolve_path(resources_raw.get("magma_bin"), base_dir=base_dir),
            precomputed_magma_prefix=resolve_path(
                resources_raw.get("precomputed_magma_prefix"),
                base_dir=base_dir,
            ),
            feature_prefix=resolve_path(resources_raw.get("feature_prefix"), base_dir=base_dir),
            raw_feature_dir=resolve_path(resources_raw.get("raw_feature_dir"), base_dir=base_dir),
            gene_annotation=resolve_path(resources_raw.get("gene_annotation"), base_dir=base_dir),
        ),
        execution=ExecutionConfig(
            mode=str(execution_raw.get("mode", "plan")),
            write_html=bool(execution_raw.get("write_html", True)),
        ),
        output=OutputConfig(
            outdir=resolve_path(str(output_raw["outdir"]), base_dir=base_dir),  # type: ignore[arg-type]
        ),
    )


def _prefix_parent_exists(path: Path | None) -> bool:
    if path is None:
        return False
    if path.exists():
        return True
    return path.parent.exists()


def validate_config(config: AppConfig) -> list[str]:
    errors: list[str] = []

    if not config.project:
        errors.append("project must not be empty")
    if not config.trait:
        errors.append("trait must not be empty")
    if config.input.sumstats is None or not config.input.sumstats.exists():
        errors.append(f"input.sumstats does not exist: {config.input.sumstats}")
    if config.input.genome_build not in ALLOWED_BUILDS:
        errors.append(f"input.genome_build must be one of {sorted(ALLOWED_BUILDS)}")
    if config.input.ancestry not in ALLOWED_ANCESTRIES:
        errors.append(f"input.ancestry must be one of {sorted(ALLOWED_ANCESTRIES)}")
    if config.execution.mode not in ALLOWED_EXECUTION_MODES:
        errors.append(f"execution.mode must be one of {sorted(ALLOWED_EXECUTION_MODES)}")

    if config.resources.magma_bin is not None and not config.resources.magma_bin.exists():
        errors.append(f"resources.magma_bin does not exist: {config.resources.magma_bin}")
    if (
        config.resources.raw_feature_dir is not None
        and not config.resources.raw_feature_dir.is_dir()
    ):
        errors.append(
            "resources.raw_feature_dir is not a directory: "
            f"{config.resources.raw_feature_dir}"
        )
    if (
        config.resources.gene_annotation is not None
        and not config.resources.gene_annotation.exists()
    ):
        errors.append(
            f"resources.gene_annotation does not exist: {config.resources.gene_annotation}"
        )
    if (
        config.resources.precomputed_magma_prefix is not None
        and not _prefix_parent_exists(config.resources.precomputed_magma_prefix)
    ):
        errors.append(
            "resources.precomputed_magma_prefix must exist or have an existing parent directory: "
            f"{config.resources.precomputed_magma_prefix}"
        )
    if (
        config.resources.feature_prefix is not None
        and not _prefix_parent_exists(config.resources.feature_prefix)
    ):
        errors.append(
            "resources.feature_prefix must exist or have an existing parent directory: "
            f"{config.resources.feature_prefix}"
        )

    if config.execution.mode == "run":
        if config.resources.gene_annotation is None:
            errors.append("resources.gene_annotation is required when execution.mode = 'run'")
        if config.resources.magma_bin is None and config.resources.precomputed_magma_prefix is None:
            errors.append(
                "set either resources.magma_bin or resources.precomputed_magma_prefix when "
                "execution.mode = 'run'"
            )
        if config.resources.feature_prefix is None and config.resources.raw_feature_dir is None:
            errors.append(
                "set either resources.feature_prefix or resources.raw_feature_dir when "
                "execution.mode = 'run'"
            )

    return errors


def write_template(path: str | Path) -> Path:
    destination = Path(path).expanduser().resolve()
    if destination.exists():
        raise ConfigError(f"Refusing to overwrite existing file: {destination}")
    destination.write_text(
        "\n".join(
            [
                'project = "demo"',
                'trait = "example_trait"',
                "",
                "[input]",
                'sumstats = "inputs/example.tsv"',
                'genome_build = "GRCh37"',
                'ancestry = "EUR"',
                "",
                "[resources]",
                '# magma_bin = "/opt/magma/magma"',
                '# precomputed_magma_prefix = "/data/magma/example_trait"',
                '# feature_prefix = "/data/features/pops_features"',
                '# raw_feature_dir = "/data/features_raw"',
                '# gene_annotation = "/data/reference/gene_annot.tsv"',
                "",
                "[execution]",
                'mode = "plan"',
                "write_html = true",
                "",
                "[output]",
                'outdir = "results/example_trait"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return destination
