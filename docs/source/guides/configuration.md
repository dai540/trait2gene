# Configuration

`trait2gene` uses TOML to avoid a runtime YAML dependency.

## Required keys

- `project`
- `trait`
- `[input]`
- `[output]`

## Required input fields

- `input.sumstats`
- `input.genome_build`
- `input.ancestry`

## Execution modes

### `plan`

Use this when you are still wiring paths. Only the input table is required.

### `run`

Use this when you want the package to materialize a real run directory. In this
mode, the config must also provide:

- `resources.gene_annotation`
- one of `resources.magma_bin` or `resources.precomputed_magma_prefix`
- one of `resources.feature_prefix` or `resources.raw_feature_dir`

