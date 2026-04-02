from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from trait2gene.config.models import AppConfig

AUTO_SENTINELS = {"auto", "", None}


def _resolve_path_like(value: str | Path, base_dir: Path) -> str | Path:
    if isinstance(value, str) and value in AUTO_SENTINELS:
        return value
    path = Path(value).expanduser() if isinstance(value, str) else value.expanduser()
    return path if path.is_absolute() else (base_dir / path).resolve()


def _resolve_optional_path_like(value: str | Path | None, base_dir: Path) -> str | Path | None:
    if value is None:
        return None
    return _resolve_path_like(value, base_dir)


def load_config(config_path: Path) -> AppConfig:
    config_path = config_path.expanduser().resolve()
    raw_text = config_path.read_text(encoding="utf-8")
    payload = yaml.safe_load(raw_text) or {}
    parsed = AppConfig.model_validate(payload)

    data: dict[str, Any] = parsed.model_dump(mode="python")
    base_dir = config_path.parent
    data["input"]["sumstats"] = _resolve_path_like(parsed.input.sumstats, base_dir)
    data["output"]["outdir"] = _resolve_path_like(parsed.output.outdir, base_dir)
    data["resources"]["magma_bin"] = _resolve_path_like(parsed.resources.magma_bin, base_dir)
    data["resources"]["reference_panel"] = _resolve_path_like(parsed.resources.reference_panel, base_dir)
    data["resources"]["gene_locations"] = _resolve_path_like(
        parsed.resources.gene_locations,
        base_dir,
    )
    data["resources"]["gene_annotation"] = _resolve_path_like(
        parsed.resources.gene_annotation,
        base_dir,
    )
    data["resources"]["feature_matrix_prefix"] = _resolve_optional_path_like(
        parsed.resources.feature_matrix_prefix,
        base_dir,
    )
    data["resources"]["raw_feature_dir"] = _resolve_optional_path_like(
        parsed.resources.raw_feature_dir,
        base_dir,
    )
    data["resources"]["control_features_path"] = _resolve_optional_path_like(
        parsed.resources.control_features_path,
        base_dir,
    )
    data["resources"]["subset_features_path"] = _resolve_optional_path_like(
        parsed.resources.subset_features_path,
        base_dir,
    )
    data["resources"]["precomputed_magma_prefix"] = _resolve_optional_path_like(
        parsed.resources.precomputed_magma_prefix,
        base_dir,
    )
    data["analysis"]["pops"]["y_path"] = _resolve_optional_path_like(parsed.analysis.pops.y_path, base_dir)
    data["analysis"]["pops"]["y_covariates_path"] = _resolve_optional_path_like(
        parsed.analysis.pops.y_covariates_path,
        base_dir,
    )
    data["analysis"]["pops"]["y_error_cov_path"] = _resolve_optional_path_like(
        parsed.analysis.pops.y_error_cov_path,
        base_dir,
    )
    data["analysis"]["prioritization"]["locus_file"] = _resolve_optional_path_like(
        parsed.analysis.prioritization.locus_file,
        base_dir,
    )
    return AppConfig.model_validate(data)
