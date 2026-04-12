from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

from trait2gene.config import ConfigError, load_config, validate_config, write_template
from trait2gene.pipeline import build_stage_plan, materialize_run
from trait2gene.version import __version__


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trait2gene",
        description="Minimal trait-to-gene run planner.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Write a minimal TOML config template.")
    init_parser.add_argument("config", type=Path)

    validate_parser = subparsers.add_parser("validate", help="Validate a TOML config.")
    validate_parser.add_argument("config", type=Path)

    plan_parser = subparsers.add_parser("plan", help="Print the derived stage plan.")
    plan_parser.add_argument("config", type=Path)
    plan_parser.add_argument("--json", action="store_true", help="Print the plan as JSON.")

    run_parser = subparsers.add_parser("run", help="Create a compact run directory.")
    run_parser.add_argument("config", type=Path)

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Report environment and optional config readiness.",
    )
    doctor_parser.add_argument("--config", type=Path, default=None)

    return parser


def _validate_or_raise(config_path: Path):
    config = load_config(config_path)
    errors = validate_config(config)
    if errors:
        raise ConfigError("\n".join(errors))
    return config


def command_init(config_path: Path) -> int:
    destination = write_template(config_path)
    print(f"Wrote template config to {destination}")
    return 0


def command_validate(config_path: Path) -> int:
    config = _validate_or_raise(config_path)
    print(f"Validation passed for {config.project}")
    return 0


def command_plan(config_path: Path, *, as_json: bool) -> int:
    config = _validate_or_raise(config_path)
    stage_plan = build_stage_plan(config)
    if as_json:
        print(json.dumps([stage.__dict__ for stage in stage_plan], indent=2))
        return 0
    print(f"Stage plan for {config.project}:")
    for stage in stage_plan:
        print(f"- {stage.name}: {stage.summary}")
    return 0


def command_run(config_path: Path) -> int:
    config = _validate_or_raise(config_path)
    config_text = config_path.expanduser().resolve().read_text(encoding="utf-8")
    outdir = materialize_run(config, config_text)
    print(f"Materialized run directory at {outdir}")
    return 0


def command_doctor(config_path: Path | None) -> int:
    payload: dict[str, object] = {
        "trait2gene_version": __version__,
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
    }
    if config_path is not None:
        try:
            config = load_config(config_path)
            payload["config"] = str(config_path.expanduser().resolve())
            payload["config_errors"] = validate_config(config)
        except ConfigError as exc:
            payload["config"] = str(config_path.expanduser().resolve())
            payload["config_errors"] = [str(exc)]
    print(json.dumps(payload, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            return command_init(args.config)
        if args.command == "validate":
            return command_validate(args.config)
        if args.command == "plan":
            return command_plan(args.config, as_json=args.json)
        if args.command == "run":
            return command_run(args.config)
        if args.command == "doctor":
            return command_doctor(args.config)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    parser.error(f"Unknown command: {args.command}")
    return 2
