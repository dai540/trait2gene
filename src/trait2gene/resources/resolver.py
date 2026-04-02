from __future__ import annotations

import shutil
import subprocess
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

from trait2gene.config.defaults import (
    AUTO_REFERENCE_PANELS,
    DEFAULT_LICENSE_NOTE,
    MAGMA_GENE_OUTPUT_SUFFIXES,
    MAGMA_REFERENCE_SUFFIXES,
)
from trait2gene.config.models import AppConfig
from trait2gene.io.features import count_feature_chunks, is_pre_munged_prefix
from trait2gene.resources.schemas import (
    FeaturesManifest,
    GeneAnnotationManifest,
    GeneLocationsManifest,
    MagmaManifest,
    ReferenceManifest,
    ResolvedManifest,
)


def _load_manifest_data(filename: str) -> dict[str, Any]:
    resource_path = resources.files("trait2gene.data.manifests").joinpath(filename)
    with resource_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _as_existing_path(value: str | Path) -> Path | None:
    if isinstance(value, str):
        if value == "auto":
            return None
        path = Path(value)
    else:
        path = value
    return path if path.exists() else None


def _prefix_has_suffixes(prefix: str | Path, suffixes: tuple[str, ...]) -> bool:
    prefix_path = Path(prefix)
    return all(prefix_path.parent.joinpath(f"{prefix_path.name}{suffix}").exists() for suffix in suffixes)


def _resolve_feature_source(config: AppConfig, feature_defaults: dict[str, Any]) -> tuple[str, str, str | None]:
    if config.resources.feature_matrix_prefix is not None:
        return ("feature_matrix_prefix", "pre_munged", str(config.resources.feature_matrix_prefix))
    if config.resources.raw_feature_dir is not None:
        return ("raw_feature_dir", "raw", str(config.resources.raw_feature_dir))
    feature_entry = feature_defaults["bundles"].get(
        config.resources.feature_bundle,
        {"format": "unknown", "prefix": "UNRESOLVED"},
    )
    return ("bundle", feature_entry["format"], feature_entry["prefix"])


def _resolve_magma_version(binary: Path | None) -> str | None:
    if binary is None:
        return None
    try:
        candidate = str(binary if binary.exists() else shutil.which(str(binary)))
        result = subprocess.run(
            [candidate, "--version"],
            check=False,
            text=True,
            capture_output=True,
        )
        text = "\n".join(filter(None, [result.stdout.strip(), result.stderr.strip()]))
    except OSError:
        return None
    first_line = text.splitlines()[0] if text.splitlines() else ""
    return first_line or None


def resolve_resources(config: AppConfig) -> ResolvedManifest:
    resource_defaults = _load_manifest_data("resources.default.yaml")
    feature_defaults = _load_manifest_data("features.default.yaml")

    magma_path = _as_existing_path(config.resources.magma_bin)
    auto_magma = shutil.which("magma") if config.resources.magma_bin == "auto" else None
    resolved_magma = magma_path or (Path(auto_magma) if auto_magma else None)
    precomputed_magma_prefix = (
        str(config.resources.precomputed_magma_prefix)
        if config.resources.precomputed_magma_prefix is not None
        else None
    )
    precomputed_status = (
        "resolved"
        if precomputed_magma_prefix
        and _prefix_has_suffixes(precomputed_magma_prefix, MAGMA_GENE_OUTPUT_SUFFIXES)
        else "unresolved"
    )
    magma_manifest = MagmaManifest(
        binary=str(resolved_magma) if resolved_magma else "auto",
        version=_resolve_magma_version(resolved_magma),
        source="external",
        license_note=DEFAULT_LICENSE_NOTE,
        precomputed_prefix=precomputed_magma_prefix,
        status="resolved"
        if resolved_magma or precomputed_status == "resolved"
        else "unresolved",
    )

    panel = (
        config.resources.reference_panel
        if config.resources.reference_panel != "auto"
        else AUTO_REFERENCE_PANELS[config.input.genome_build][config.input.ancestry]
    )
    reference_defaults = resource_defaults["reference_panels"][config.input.genome_build][
        config.input.ancestry
    ]
    reference_prefix = (
        str(config.resources.reference_panel)
        if config.resources.reference_panel != "auto"
        else reference_defaults.get("path_prefix", "UNRESOLVED")
    )
    reference_status = (
        "resolved" if _prefix_has_suffixes(reference_prefix, MAGMA_REFERENCE_SUFFIXES) else "unresolved"
    )
    reference_manifest = ReferenceManifest(
        panel=str(panel),
        build=config.input.genome_build,
        path_prefix=reference_prefix,
        source_url=reference_defaults.get("source_url"),
        status=reference_status,
    )

    default_gene_loc = resource_defaults["gene_locations"][config.input.genome_build]
    gene_loc_path = (
        str(config.resources.gene_locations)
        if config.resources.gene_locations != "auto"
        else default_gene_loc["path"]
    )
    gene_locations_manifest = GeneLocationsManifest(
        build=config.input.genome_build,
        path=gene_loc_path,
        status="resolved" if Path(gene_loc_path).exists() else "unresolved",
    )

    default_gene_annot = resource_defaults["gene_annotation"][config.input.genome_build]
    gene_annotation_path = (
        str(config.resources.gene_annotation)
        if config.resources.gene_annotation != "auto"
        else default_gene_annot["path"]
    )
    gene_annotation_manifest = GeneAnnotationManifest(
        name=default_gene_annot["name"],
        path=gene_annotation_path,
        status="resolved" if Path(gene_annotation_path).exists() else "unresolved",
    )

    feature_source, feature_format, feature_location = _resolve_feature_source(config, feature_defaults)
    feature_prefix = feature_location or "UNRESOLVED"
    feature_status = "unresolved"
    feature_chunks = 0
    raw_dir = None
    if feature_format == "pre_munged" and feature_location:
        feature_status = "resolved" if is_pre_munged_prefix(Path(feature_location)) else "unresolved"
        feature_chunks = count_feature_chunks(Path(feature_location))
    elif feature_format == "raw" and feature_location:
        raw_dir = feature_location
        feature_status = "resolved" if Path(feature_location).is_dir() else "unresolved"

    feature_manifest = FeaturesManifest(
        bundle=config.resources.feature_bundle,
        format=feature_format,
        prefix=feature_prefix,
        num_feature_chunks=feature_chunks,
        source=feature_source,
        raw_dir=raw_dir,
        status=feature_status,
    )

    return ResolvedManifest(
        magma=magma_manifest,
        reference=reference_manifest,
        gene_locations=gene_locations_manifest,
        gene_annotation=gene_annotation_manifest,
        features=feature_manifest,
    )
