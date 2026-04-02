# Quickstart

## Minimal validation flow

Start from the bundled minimal config:

```bash
trait2gene validate src/trait2gene/data/examples/config.minimal.yaml
trait2gene fetch-resources src/trait2gene/data/examples/config.minimal.yaml
```

## Full-run templates

For real runs, start from one of these templates:

- `src/trait2gene/data/examples/config.realpaths.template.yaml`
- `src/trait2gene/data/examples/config.precomputed.template.yaml`

The most common execution flow is:

```bash
trait2gene validate config.yaml
trait2gene doctor --config config.yaml
trait2gene run config.yaml
```

## Standard pipeline order

`trait2gene run` executes stages in this order:

1. `validate`
2. `prepare`
3. `magma`
4. `feature_prep`
5. `pops`
6. `prioritize`
7. `report`

If the config uses a custom `y_path`, or precomputed MAGMA outputs, the stage
plan adjusts automatically to skip unnecessary work while keeping output layout
and reporting consistent.

## Public example

To reproduce the bundled real-data tutorial:

```bash
python scripts/run_public_schizophrenia_example.py
```

