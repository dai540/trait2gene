from __future__ import annotations

import subprocess
from pathlib import Path

from trait2gene.config.defaults import DEFAULT_FEATURE_PREFIX_BASENAME, MAGMA_GENE_OUTPUT_SUFFIXES
from trait2gene.config.loader import load_config
from trait2gene.engine.logging import console
from trait2gene.engine.provenance import write_json
from trait2gene.engine.shell import resolve_executable_command, run_command
from trait2gene.io.features import count_feature_chunks, is_pre_munged_prefix
from trait2gene.io.outputs import ensure_output_layout
from trait2gene.resources.resolver import resolve_resources

MAX_POPS_ATTEMPTS = 2


def _append_bool_flag(args: list[str], *, enabled: bool, true_flag: str, false_flag: str) -> None:
    args.append(true_flag if enabled else false_flag)


def _append_list_flag(args: list[str], flag: str, values: list[str] | None) -> None:
    if values:
        args.append(flag)
        args.extend([str(value) for value in values])


def _resolve_gene_annotation_path(config, manifest) -> Path:
    candidate = (
        config.resources.gene_annotation
        if config.resources.gene_annotation != "auto"
        else manifest.gene_annotation.path
    )
    path = Path(candidate)
    if not path.exists():
        raise RuntimeError("Gene annotation file is unresolved. Set resources.gene_annotation.")
    return path


def _resolve_feature_prefix(config, manifest, layout) -> Path:
    prepared_prefix = layout["features"] / DEFAULT_FEATURE_PREFIX_BASENAME
    if is_pre_munged_prefix(prepared_prefix):
        return prepared_prefix
    if config.resources.feature_matrix_prefix is not None and is_pre_munged_prefix(Path(config.resources.feature_matrix_prefix)):
        return Path(config.resources.feature_matrix_prefix)
    if manifest.features.format == "pre_munged" and is_pre_munged_prefix(Path(manifest.features.prefix)):
        return Path(manifest.features.prefix)
    raise RuntimeError("No prepared feature prefix was found. Run prep-features first or set resources.feature_matrix_prefix.")


def _resolve_magma_prefix(config, layout) -> Path | None:
    prepared_prefix = layout["magma"] / config.trait
    if all(Path(f"{prepared_prefix}{suffix}").exists() for suffix in MAGMA_GENE_OUTPUT_SUFFIXES):
        return prepared_prefix
    if config.resources.precomputed_magma_prefix is not None:
        source_prefix = Path(config.resources.precomputed_magma_prefix)
        if all(Path(f"{source_prefix}{suffix}").exists() for suffix in MAGMA_GENE_OUTPUT_SUFFIXES):
            return source_prefix
    return None


def _write_pops_attempt_logs(layout: dict[str, Path], attempt: int, stdout: str | None, stderr: str | None) -> None:
    stdout_text = stdout or ""
    stderr_text = stderr or ""
    (layout["metadata"] / f"pops.attempt-{attempt}.stdout.log").write_text(stdout_text, encoding="utf-8")
    (layout["metadata"] / f"pops.attempt-{attempt}.stderr.log").write_text(stderr_text, encoding="utf-8")
    (layout["metadata"] / "pops.stdout.log").write_text(stdout_text, encoding="utf-8")
    (layout["metadata"] / "pops.stderr.log").write_text(stderr_text, encoding="utf-8")


def _run_pops_command(command: list[str], layout: dict[str, Path]) -> subprocess.CompletedProcess[str]:
    last_error: subprocess.CalledProcessError | None = None
    for attempt in range(1, MAX_POPS_ATTEMPTS + 1):
        try:
            result = run_command(command)
        except subprocess.CalledProcessError as exc:
            _write_pops_attempt_logs(layout, attempt, exc.stdout, exc.stderr)
            last_error = exc
            if attempt == MAX_POPS_ATTEMPTS:
                stderr = (exc.stderr or "").strip()
                stdout = (exc.stdout or "").strip()
                detail = stderr or stdout or "No stdout/stderr captured."
                raise RuntimeError(f"PoPS command failed after {attempt} attempts. {detail}") from exc
            console.print(
                "[yellow]PoPS command failed on first attempt; retrying once with the same inputs.[/yellow]"
            )
            continue
        _write_pops_attempt_logs(layout, attempt, result.stdout, result.stderr)
        return result
    raise RuntimeError("PoPS command failed before any attempt completed.") from last_error


def run_pops(config_path: Path) -> dict[str, str | int]:
    config = load_config(config_path)
    layout = ensure_output_layout(config.output.outdir)
    manifest = resolve_resources(config)
    feature_prefix = _resolve_feature_prefix(config, manifest, layout)
    magma_prefix = _resolve_magma_prefix(config, layout)
    out_prefix = layout["pops"] / config.trait
    vendor_script = Path(__file__).resolve().parents[1] / "vendor" / "pops_upstream" / "pops.py"

    args: list[str] = [
        "--gene_annot_path",
        str(_resolve_gene_annotation_path(config, manifest)),
        "--feature_mat_prefix",
        str(feature_prefix),
        "--num_feature_chunks",
        str(count_feature_chunks(feature_prefix)),
        "--method",
        config.analysis.pops.method,
        "--out_prefix",
        str(out_prefix),
        "--random_seed",
        str(config.analysis.pops.random_seed),
        "--feature_selection_p_cutoff",
        str(config.analysis.pops.feature_selection_p_cutoff),
    ]

    if magma_prefix is not None:
        args.extend(["--magma_prefix", str(magma_prefix)])
        _append_bool_flag(
            args,
            enabled=config.analysis.pops.use_magma_covariates,
            true_flag="--use_magma_covariates",
            false_flag="--ignore_magma_covariates",
        )
        _append_bool_flag(
            args,
            enabled=config.analysis.pops.use_magma_error_cov,
            true_flag="--use_magma_error_cov",
            false_flag="--ignore_magma_error_cov",
        )
    elif config.analysis.pops.y_path is not None:
        args.extend(["--y_path", str(config.analysis.pops.y_path)])
        if config.analysis.pops.y_covariates_path is not None:
            args.extend(["--y_covariates_path", str(config.analysis.pops.y_covariates_path)])
        if config.analysis.pops.y_error_cov_path is not None:
            args.extend(["--y_error_cov_path", str(config.analysis.pops.y_error_cov_path)])
    else:
        raise RuntimeError("No MAGMA prefix or custom y_path was available for PoPS.")

    _append_bool_flag(
        args,
        enabled=config.analysis.pops.remove_hla,
        true_flag="--project_out_covariates_remove_hla",
        false_flag="--project_out_covariates_keep_hla",
    )
    _append_bool_flag(
        args,
        enabled=config.analysis.pops.remove_hla,
        true_flag="--feature_selection_remove_hla",
        false_flag="--feature_selection_keep_hla",
    )
    _append_bool_flag(
        args,
        enabled=config.analysis.pops.remove_hla,
        true_flag="--training_remove_hla",
        false_flag="--training_keep_hla",
    )
    _append_list_flag(
        args,
        "--project_out_covariates_chromosomes",
        config.analysis.pops.project_out_covariates_chromosomes,
    )
    _append_list_flag(
        args,
        "--feature_selection_chromosomes",
        config.analysis.pops.feature_selection_chromosomes,
    )
    _append_list_flag(
        args,
        "--training_chromosomes",
        config.analysis.pops.training_chromosomes,
    )
    if config.analysis.pops.feature_selection_max_num is not None:
        args.extend(["--feature_selection_max_num", str(config.analysis.pops.feature_selection_max_num)])
    if config.analysis.pops.feature_selection_fss_num_features is not None:
        args.extend(
            [
                "--feature_selection_fss_num_features",
                str(config.analysis.pops.feature_selection_fss_num_features),
            ]
        )
    if config.resources.control_features_path is not None:
        args.extend(["--control_features_path", str(config.resources.control_features_path)])
    if config.resources.subset_features_path is not None:
        args.extend(["--subset_features_path", str(config.resources.subset_features_path)])
    if config.analysis.pops.save_matrix_files:
        args.append("--save_matrix_files")
    if config.analysis.pops.verbose:
        args.append("--verbose")

    command = resolve_executable_command(vendor_script, *args)
    payload = {
        "trait": config.trait,
        "feature_prefix": str(feature_prefix),
        "magma_prefix": str(magma_prefix) if magma_prefix is not None else None,
        "vendor_script": str(vendor_script),
        "command": command,
        "max_attempts": MAX_POPS_ATTEMPTS,
    }
    write_json(layout["metadata"] / "pops_plan.json", payload)
    _run_pops_command(command, layout)

    for suffix in (".preds", ".coefs", ".marginals"):
        if not Path(f"{out_prefix}{suffix}").exists():
            raise RuntimeError(f"PoPS did not produce expected output: {out_prefix}{suffix}")

    console.print(f"[green]PoPS outputs written[/green] to {out_prefix.parent}")
    return {
        "trait": config.trait,
        "feature_prefix": str(feature_prefix),
        "num_feature_chunks": count_feature_chunks(feature_prefix),
        "out_prefix": str(out_prefix),
    }
