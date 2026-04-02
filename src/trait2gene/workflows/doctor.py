from __future__ import annotations

import shutil
from pathlib import Path

from trait2gene.config.loader import load_config
from trait2gene.engine.shell import resolve_executable_command, run_command
from trait2gene.resources.cache import get_cache_dir
from trait2gene.resources.resolver import resolve_resources


def _cache_writable(cache_dir: Path) -> bool:
    probe = cache_dir / ".write_test"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def run_doctor(config_path: Path | None = None) -> dict[str, object]:
    cache_dir = get_cache_dir()
    magma_path = shutil.which("magma")
    magma_probe = None
    if magma_path:
        probe_result = run_command(
            resolve_executable_command(magma_path, "--help"),
            check=False,
        )
        magma_probe = {"returncode": probe_result.returncode}
    payload: dict[str, object] = {
        "python": shutil.which("python"),
        "magma_on_path": magma_path,
        "magma_probe": magma_probe,
        "cache_dir": str(cache_dir),
        "cache_writable": _cache_writable(cache_dir),
        "vendor_pops_script": str(
            Path(__file__).resolve().parents[1] / "vendor" / "pops_upstream" / "pops.py"
        ),
        "vendor_feature_script": str(
            Path(__file__).resolve().parents[1]
            / "vendor"
            / "pops_upstream"
            / "munge_feature_directory.py"
        ),
    }

    if config_path:
        config = load_config(config_path)
        payload["config"] = {
            "project": config.project,
            "trait": config.trait,
            "outdir": str(config.output.outdir),
        }
        payload["resolved_manifest"] = resolve_resources(config).model_dump(mode="python")

    return payload
