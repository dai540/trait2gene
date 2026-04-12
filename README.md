# trait2gene

`trait2gene` is a compact Python package for validating and materializing
trait-to-gene analysis run plans without bundling heavy upstream engines,
example datasets, or generated artifacts. The repository is intentionally kept
small: standard-library runtime code, Sphinx documentation, minimal tests, and
GitHub workflows only.

[![CI](https://github.com/dai540/trait2gene/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/dai540/trait2gene/actions/workflows/ci.yml)
[![Docs](https://github.com/dai540/trait2gene/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/dai540/trait2gene/actions/workflows/docs.yml)
[![Docs Site](https://img.shields.io/badge/docs-GitHub%20Pages-1f5f8b)](https://dai540.github.io/trait2gene/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB)](https://www.python.org/)

[Documentation](https://dai540.github.io/trait2gene/) |
[Getting Started](https://dai540.github.io/trait2gene/getting-started/installation.html) |
[Guides](https://dai540.github.io/trait2gene/guides/configuration.html) |
[Tutorials](https://dai540.github.io/trait2gene/tutorials/minimal-local-run.html) |
[Reference](https://dai540.github.io/trait2gene/reference/index.html)

## Purpose

This rebuild is intentionally minimal.

- No vendored MAGMA binaries
- No vendored PoPS source tree
- No downloaded demo or real datasets
- No cached run outputs
- No generated documentation checked into the package tree
- No large feature matrices, reports, or temporary artifacts

The repository keeps only what is necessary to install the package, validate a
configuration, generate a run plan, materialize a lightweight output skeleton,
build documentation, and verify the code in CI.

## Scope

`trait2gene` provides a small CLI around a TOML configuration file.

- `trait2gene init` writes a minimal config template
- `trait2gene validate` checks that the config is coherent
- `trait2gene plan` renders the stage plan
- `trait2gene run` creates a standardized run directory with metadata and
  report stubs
- `trait2gene doctor` reports local environment and config readiness

The package does not bundle heavy analysis engines. That tradeoff is explicit:
repository size stays small, and the package remains easy to audit, install,
and maintain.

## Install

Core install:

```bash
pip install -e .
trait2gene --help
```

Developer install:

```bash
pip install -e .[dev,docs]
```

Build docs locally:

```bash
python scripts/build_docs.py
```

## Quick Start

1. Create a config template.

```bash
trait2gene init config.toml
```

2. Point `input.sumstats` to a real local TSV file.

3. Validate the config.

```bash
trait2gene validate config.toml
```

4. Inspect the planned stages.

```bash
trait2gene plan config.toml
```

5. Materialize a minimal run directory.

```bash
trait2gene run config.toml
```

The command above does not download data and does not vendor external engines.
It writes a compact run skeleton under `output.outdir`.

## Configuration Model

The package uses TOML to stay dependency-light. A minimal example:

```toml
project = "demo"
trait = "bmi"

[input]
sumstats = "inputs/demo.tsv"
genome_build = "GRCh37"
ancestry = "EUR"

[resources]
precomputed_magma_prefix = "/data/magma/demo"
feature_prefix = "/data/features/pops_features"
gene_annotation = "/data/reference/gene_annot.tsv"

[execution]
mode = "plan"
write_html = true

[output]
outdir = "results/demo"
```

Key design points:

- `execution.mode = "plan"` keeps validation permissive for early setup
- `execution.mode = "run"` requires the minimum resource fields needed for a
  real external-tool handoff
- relative paths are resolved relative to the config file location
- the package checks concrete files aggressively but treats prefix-style paths
  pragmatically, because MAGMA and feature prefixes usually point to file
  families rather than a single file

## Output Layout

`trait2gene run` creates only a small standardized layout:

```text
results/demo/
├── metadata/
│   ├── config.snapshot.toml
│   ├── run-summary.json
│   └── stage-plan.json
└── reports/
    ├── summary.md
    └── index.html
```

This is deliberate. The package does not ship heavy intermediate outputs or
generated data. If you integrate external MAGMA or PoPS execution later, the
same output root can be extended without changing the top-level contract.

## Documentation

The Sphinx site is organized into four stable sections:

- `Getting Started`
  Installation and quickstart
- `Guides`
  Configuration and CLI behavior
- `Tutorials`
  Minimal local usage and external-tool dry-run workflows
- `Reference`
  CLI and Python API notes

Source files live under `docs/source/`. Built HTML is intentionally ignored and
not committed to keep the tree small.

## Repository Policy

This repository follows a strict size policy:

- keep runtime dependencies minimal
- keep package files minimal
- remove generated build artifacts
- remove downloaded datasets
- remove temporary directories
- avoid checking in anything that materially inflates repository size

That policy is why the package is a compact scaffold rather than a bundled
analysis distribution.

## Development

Run tests:

```bash
python -m pytest
```

Run lint:

```bash
python -m ruff check .
```

Build docs:

```bash
python scripts/build_docs.py
```

## License

MIT. See [LICENSE](LICENSE).

