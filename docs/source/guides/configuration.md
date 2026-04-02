# Configuration Guide

`trait2gene` configuration is YAML backed by strict Pydantic validation.

## Minimum required fields

- `project`
- `trait`
- `input.sumstats`
- `input.genome_build`
- `input.ancestry`
- `output.outdir`

## Example templates

Use these bundled templates as starting points:

- `src/trait2gene/data/examples/config.realpaths.template.yaml`
- `src/trait2gene/data/examples/config.precomputed.template.yaml`
- `src/trait2gene/data/examples/config.minimal.yaml`

## Common path fields

These usually need explicit absolute paths in production:

- `input.sumstats`
- `resources.magma_bin`
- `resources.reference_panel`
- `resources.gene_locations`
- `resources.gene_annotation`
- `resources.feature_matrix_prefix`
- `resources.raw_feature_dir`
- `resources.precomputed_magma_prefix`
- `resources.control_features_path`
- `resources.subset_features_path`
- `analysis.prioritization.locus_file`
- `output.outdir`

## Prefix semantics

Some config entries are prefixes rather than single files.

### `resources.reference_panel`

This must point to a PLINK prefix. If the prefix is:

`/data/reference/1000g/eas/g1000_eas`

then these files must exist:

- `/data/reference/1000g/eas/g1000_eas.bed`
- `/data/reference/1000g/eas/g1000_eas.bim`
- `/data/reference/1000g/eas/g1000_eas.fam`

### `resources.precomputed_magma_prefix`

This must point to a MAGMA prefix with:

- `.genes.out`
- `.genes.raw`

### `resources.feature_matrix_prefix`

This must point to the prefix written by the upstream feature munging step,
including:

- `.rows.txt`
- `.cols.*.txt`
- `.mat.*.npy`

## Modes

### `standard`

Use this when you want the most guided experience:

- external MAGMA execution
- pre-munged feature bundle
- standard output layout

### `advanced`

Use this when you need to supply custom resources such as:

- precomputed MAGMA outputs
- raw feature directories
- custom `y_path`
- custom locus files

## Upstream-aligned defaults

PoPS settings default to:

- `method = ridge`
- `use_magma_covariates = true`
- `use_magma_error_cov = true`
- `remove_hla = true`

