# CLI Guide

## Main commands

- `trait2gene run CONFIG`
- `trait2gene validate CONFIG`
- `trait2gene fetch-resources CONFIG`
- `trait2gene run-magma CONFIG`
- `trait2gene prep-features CONFIG`
- `trait2gene run-pops CONFIG`
- `trait2gene prioritize CONFIG`
- `trait2gene report CONFIG`
- `trait2gene inspect outputs PATH`
- `trait2gene doctor`

## Recommended full-run flow

Before a production run:

```bash
trait2gene validate config.yaml
trait2gene doctor --config config.yaml
trait2gene fetch-resources config.yaml
trait2gene run config.yaml
```

## Precomputed MAGMA flow

If `.genes.out` and `.genes.raw` already exist:

```bash
trait2gene validate config.precomputed.yaml
trait2gene run-pops config.precomputed.yaml
trait2gene prioritize config.precomputed.yaml
trait2gene report config.precomputed.yaml
```

## `doctor`

`doctor` inspects environment and optional config wiring, including:

- Python runtime basics
- MAGMA reachability
- cache and output writability
- resolved resources when a config is supplied

## `inspect outputs`

`trait2gene inspect outputs PATH` summarizes the standard output layout under a
results directory and reports whether each expected section exists.

