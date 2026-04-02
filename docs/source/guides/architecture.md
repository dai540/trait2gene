# Architecture

`trait2gene` is structured as a thin Python orchestration layer around external
MAGMA and upstream-compatible PoPS components.

## Core responsibilities

The package owns:

- the CLI surface and command routing
- config parsing and validation
- resource resolution and manifest writing
- standardized output layout
- provenance and run metadata
- locus prioritization and report generation

MAGMA stays external, and PoPS compatibility is preserved through vendored
upstream scripts plus a small compatibility layer.

## Execution model

The full pipeline follows this high-level sequence:

1. validate config and input contracts
2. resolve resources and write manifests
3. run or copy MAGMA outputs
4. prepare feature matrices
5. execute PoPS
6. prioritize genes within loci
7. write tables, metadata, and reports

## Package layout

Important package areas:

- `trait2gene.cli`
  CLI commands and Typer app wiring
- `trait2gene.config`
  Pydantic models and config loaders
- `trait2gene.resources`
  manifest and resource resolution helpers
- `trait2gene.engine`
  planning, logging, provenance, and pipeline orchestration
- `trait2gene.workflows`
  stage implementations
- `trait2gene.domain`
  loci, ranking, and QC helpers
- `trait2gene.report`
  HTML and table rendering
- `trait2gene.vendor`
  vendored upstream PoPS scripts

## Why the stages stay separate

Each stage is exposed as its own command so you can:

- validate configs without running heavy steps
- reuse precomputed MAGMA outputs
- prepare features independently of PoPS
- rerun reporting or prioritization on existing outputs

