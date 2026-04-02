from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import typer

from trait2gene.config.defaults import OUTPUT_LAYOUT
from trait2gene.engine.logging import console, err_console
from trait2gene.engine.runner import run_pipeline
from trait2gene.workflows.doctor import run_doctor
from trait2gene.workflows.feature_stage import run_feature_prep
from trait2gene.workflows.magma_stage import run_magma
from trait2gene.workflows.pops_stage import run_pops
from trait2gene.workflows.prepare import run_prepare
from trait2gene.workflows.prioritize_stage import run_prioritize
from trait2gene.workflows.report_stage import run_report
from trait2gene.workflows.validate import run_validate

app = typer.Typer(
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    help="End-to-end PoPS-oriented GWAS gene prioritization CLI.",
)
inspect_app = typer.Typer(no_args_is_help=True, help="Inspect standardized outputs.")
app.add_typer(inspect_app, name="inspect")
DOCTOR_CONFIG_OPTION = typer.Option(None, "--config", "-c")


def _invoke(action: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    try:
        return action(*args, **kwargs)
    except Exception as exc:  # pragma: no cover - exercised via CLI tests
        err_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


@app.command()
def run(config: Path) -> None:
    """Run the full pipeline."""
    _invoke(run_pipeline, config)
    console.print("[green]Pipeline completed.[/green]")


@app.command("validate")
def validate_cmd(config: Path) -> None:
    """Validate config and input contracts."""
    _invoke(run_validate, config)


@app.command("fetch-resources")
def fetch_resources_cmd(config: Path) -> None:
    """Resolve resources and write the manifest."""
    _invoke(run_prepare, config)


@app.command("run-magma")
def run_magma_cmd(config: Path) -> None:
    """Plan the MAGMA stage."""
    _invoke(run_magma, config)


@app.command("prep-features")
def prep_features_cmd(config: Path) -> None:
    """Prepare or validate feature bundles."""
    _invoke(run_feature_prep, config)


@app.command("run-pops")
def run_pops_cmd(config: Path) -> None:
    """Plan the PoPS stage."""
    _invoke(run_pops, config)


@app.command("prioritize")
def prioritize_cmd(config: Path) -> None:
    """Produce locus-level prioritized genes."""
    _invoke(run_prioritize, config)


@app.command("report")
def report_cmd(config: Path) -> None:
    """Render report assets from current outputs."""
    _invoke(run_report, config)


@app.command()
def doctor(config: Path | None = DOCTOR_CONFIG_OPTION) -> None:
    """Inspect environment health and optional config wiring."""
    payload = _invoke(run_doctor, config)
    console.print_json(data=payload)


@inspect_app.command("outputs")
def inspect_outputs(path: Path) -> None:
    """Summarize a standardized output directory."""
    resolved = path.expanduser().resolve()
    summary: dict[str, dict[str, Any]] = {}
    for name, relative in OUTPUT_LAYOUT.items():
        candidate = resolved / relative
        summary[name] = {
            "path": str(candidate),
            "exists": candidate.exists(),
            "file_count": len(list(candidate.glob("*"))) if candidate.exists() else 0,
        }
    console.print_json(data=summary)
