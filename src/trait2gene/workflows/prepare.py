from __future__ import annotations

from pathlib import Path

from trait2gene.config.loader import load_config
from trait2gene.domain.qc import qc_payload
from trait2gene.engine.logging import console
from trait2gene.engine.plan import required_resource_sections
from trait2gene.engine.provenance import software_versions, timestamp_utc, write_json
from trait2gene.io.outputs import ensure_output_layout
from trait2gene.resources.manifest import write_resolved_manifest
from trait2gene.resources.resolver import resolve_resources


def run_prepare(config_path: Path):
    config = load_config(config_path)
    layout = ensure_output_layout(config.output.outdir)
    manifest = resolve_resources(config)

    write_resolved_manifest(layout["metadata"] / "resolved_manifest.yaml", manifest)
    write_json(layout["metadata"] / "software_versions.json", software_versions())

    unresolved = [
        key
        for key, section in manifest.model_dump(mode="python").items()
        if key in required_resource_sections(config)
        and isinstance(section, dict)
        and section.get("status") == "unresolved"
    ]
    resource_qc = qc_payload(
        status="ok" if not unresolved else "warning",
        errors=[],
        warnings=[f"Unresolved resources: {', '.join(unresolved)}"] if unresolved else [],
        details={"prepared_at": timestamp_utc(), "manifest": manifest.model_dump(mode="python")},
    )
    write_json(layout["qc"] / "resource_qc.json", resource_qc)
    console.print(f"[green]Wrote manifest[/green] to {layout['metadata'] / 'resolved_manifest.yaml'}")
    return manifest
