from __future__ import annotations

import shutil
from pathlib import Path

from trait2gene.config.defaults import MAGMA_GENE_OUTPUT_SUFFIXES
from trait2gene.config.loader import load_config
from trait2gene.config.models import AppConfig
from trait2gene.domain.qc import qc_payload
from trait2gene.engine.logging import console
from trait2gene.engine.plan import required_resource_sections, requires_magma_execution
from trait2gene.engine.provenance import timestamp_utc, write_json
from trait2gene.io.features import is_pre_munged_prefix
from trait2gene.io.outputs import ensure_output_layout
from trait2gene.io.sumstats import missing_columns, read_sumstats_header
from trait2gene.resources.resolver import resolve_resources


def _validate_optional_file(path: str | Path | None, label: str, errors: list[str]) -> None:
    if path is not None and not Path(path).exists():
        errors.append(f"{label} does not exist: {path}")


def _validate_optional_dir(path: str | Path | None, label: str, errors: list[str]) -> None:
    if path is not None and not Path(path).is_dir():
        errors.append(f"{label} does not exist or is not a directory: {path}")


def _validate_prefix_outputs(prefix: str | Path | None, suffixes: tuple[str, ...], label: str, errors: list[str]) -> None:
    if prefix is None:
        return
    prefix_path = Path(prefix)
    if not all((prefix_path.parent / f"{prefix_path.name}{suffix}").exists() for suffix in suffixes):
        errors.append(f"{label} is missing one or more expected files for prefix: {prefix}")


def _validate_stage_specific_paths(config: AppConfig, errors: list[str]) -> None:
    _validate_optional_file(config.resources.control_features_path, "Control features file", errors)
    _validate_optional_file(config.resources.subset_features_path, "Subset features file", errors)
    _validate_prefix_outputs(
        config.resources.precomputed_magma_prefix,
        MAGMA_GENE_OUTPUT_SUFFIXES,
        "Precomputed MAGMA prefix",
        errors,
    )
    _validate_optional_file(config.analysis.pops.y_path, "Custom y_path", errors)
    _validate_optional_file(config.analysis.pops.y_covariates_path, "Custom y_covariates_path", errors)
    _validate_optional_file(config.analysis.pops.y_error_cov_path, "Custom y_error_cov_path", errors)
    _validate_optional_dir(config.resources.raw_feature_dir, "Raw feature directory", errors)
    if config.resources.feature_matrix_prefix is not None and not is_pre_munged_prefix(
        Path(config.resources.feature_matrix_prefix)
    ):
        errors.append(
            f"Feature matrix prefix is missing .rows/.mat/.cols artifacts: {config.resources.feature_matrix_prefix}"
        )

    if config.analysis.prioritization.mode == "locus_file":
        if config.analysis.prioritization.locus_file is None:
            errors.append("analysis.prioritization.locus_file is required when mode=locus_file.")
        else:
            _validate_optional_file(
                config.analysis.prioritization.locus_file,
                "Locus file",
                errors,
            )


def run_validate(config_path: Path) -> AppConfig:
    config = load_config(config_path)
    layout = ensure_output_layout(config.output.outdir)
    errors: list[str] = []
    warnings: list[str] = []
    details: dict[str, object] = {"validated_at": timestamp_utc()}

    if not config.input.sumstats.exists():
        errors.append(f"Summary statistics file does not exist: {config.input.sumstats}")
    else:
        header = read_sumstats_header(config.input.sumstats)
        details["sumstats_columns"] = header
        missing = missing_columns(header, config)
        if missing:
            errors.append(f"Missing required summary statistic columns: {', '.join(missing)}")

    magma_bin = config.resources.magma_bin
    if isinstance(magma_bin, Path) and not magma_bin.exists():
        errors.append(f"MAGMA binary does not exist: {magma_bin}")
    elif requires_magma_execution(config) and magma_bin == "auto" and shutil.which("magma") is None:
        warnings.append("MAGMA binary was not found on PATH. Set resources.magma_bin before execution.")

    _validate_stage_specific_paths(config, errors)

    manifest = resolve_resources(config)
    required_sections = required_resource_sections(config)
    unresolved = [
        name
        for name, section in manifest.model_dump(mode="python").items()
        if name in required_sections and isinstance(section, dict) and section.get("status") == "unresolved"
    ]
    if unresolved:
        warnings.append(f"Some resources are unresolved: {', '.join(unresolved)}")
    details["resolved_resources"] = manifest.model_dump(mode="python")

    payload = qc_payload(
        status="ok" if not errors else "error",
        errors=errors,
        warnings=warnings,
        details=details,
    )
    write_json(layout["qc"] / "input_qc.json", payload)

    if errors:
        raise ValueError("Validation failed. " + " ".join(errors))

    console.print(f"[green]Validation passed[/green] for {config.project}")
    for warning in warnings:
        console.print(f"[yellow]Warning:[/yellow] {warning}")
    return config
