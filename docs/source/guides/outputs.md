# Output Layout

Every run writes into a standardized output root.

## Top-level layout

- `qc/`
- `work/normalized/`
- `work/magma/`
- `work/features/`
- `work/pops/`
- `tables/`
- `reports/`
- `metadata/`

## What each section contains

### `qc/`

- input validation summaries
- resource resolution QC summaries

### `work/magma/`

- MAGMA annotation products
- `<trait>.genes.out`
- `<trait>.genes.raw`

### `work/features/`

- munged PoPS feature matrices
- `.rows.txt`
- `.cols.*.txt`
- `.mat.*.npy`

### `work/pops/`

- `<trait>.preds`
- `<trait>.coefs`
- `<trait>.marginals`

### `tables/`

- `prioritized_genes.tsv`
- `all_genes_ranked.tsv`
- `top_features.tsv`

### `reports/`

- `report.html`
- `summary.json`

### `metadata/`

- `resolved_manifest.yaml`
- `run_metadata.json`
- `software_versions.json`

## Why this layout matters

The standardized layout keeps intermediate products inspectable while still
supporting a simple end-to-end CLI. It also makes stage reruns predictable:

- reporting can rerun from existing PoPS outputs
- prioritization can rerun with different locus definitions
- manifests and metadata preserve provenance for debugging and reproducibility

