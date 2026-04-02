from __future__ import annotations

from trait2gene.config.models import AppConfig


def uses_precomputed_magma(config: AppConfig) -> bool:
    return config.resources.precomputed_magma_prefix is not None


def uses_custom_y(config: AppConfig) -> bool:
    return config.analysis.pops.y_path is not None


def requires_magma_execution(config: AppConfig) -> bool:
    return not uses_precomputed_magma(config) and not uses_custom_y(config)


def planned_stage_functions(config: AppConfig):
    from trait2gene.workflows.feature_stage import run_feature_prep
    from trait2gene.workflows.magma_stage import run_magma
    from trait2gene.workflows.pops_stage import run_pops
    from trait2gene.workflows.prepare import run_prepare
    from trait2gene.workflows.prioritize_stage import run_prioritize
    from trait2gene.workflows.report_stage import run_report
    from trait2gene.workflows.validate import run_validate

    stages = [
        ("validate", run_validate),
        ("prepare", run_prepare),
    ]
    if requires_magma_execution(config) or uses_precomputed_magma(config):
        stages.append(("magma", run_magma))
    stages.extend(
        [
            ("feature_prep", run_feature_prep),
            ("pops", run_pops),
            ("prioritize", run_prioritize),
            ("report", run_report),
        ]
    )
    return stages


def required_resource_sections(config: AppConfig) -> set[str]:
    required = {"gene_annotation", "features"}
    if uses_precomputed_magma(config):
        required.add("magma")
    elif requires_magma_execution(config):
        required.update({"magma", "reference", "gene_locations"})
    return required
