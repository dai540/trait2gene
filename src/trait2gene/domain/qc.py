from __future__ import annotations


def qc_payload(*, status: str, errors: list[str], warnings: list[str], details: dict[str, object]) -> dict[str, object]:
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "details": details,
    }
