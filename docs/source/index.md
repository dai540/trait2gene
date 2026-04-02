# trait2gene

`trait2gene` is a Python package and CLI for end-to-end PoPS-style GWAS gene
prioritization. It standardizes config validation, resource resolution, MAGMA
handoff, feature preparation, PoPS execution, locus-level ranking, and report
generation behind one reproducible workflow.

```{toctree}
:maxdepth: 2
:caption: Getting Started

installation
quickstart
```

```{toctree}
:maxdepth: 2
:caption: Guides

guides/architecture
guides/cli
guides/configuration
guides/outputs
```

```{toctree}
:maxdepth: 2
:caption: Tutorials

tutorials/index
```

```{toctree}
:maxdepth: 2
:caption: Reference

reference/api
```

## Highlights

- External MAGMA execution without redistributing MAGMA itself
- Upstream-compatible PoPS wrapping with standardized intermediate outputs
- Strict YAML configuration via Pydantic models
- Locus prioritization and HTML reporting on top of PoPS outputs
- Reproducible public example using real downloaded data

## Real public example

The repository includes a full public schizophrenia walkthrough. It downloads
public inputs, writes a machine-local config, runs the pipeline using
precomputed MAGMA outputs, and verifies that `trait2gene` reproduces the public
upstream PoPS results.

```bash
python scripts/run_public_schizophrenia_example.py
```

Key artifacts:

- `real_runs/schizophrenia_public_example/results/reports/report.html`
- `real_runs/schizophrenia_public_example/verification_summary.json`
- `real_runs/schizophrenia_public_example/result_snapshot.json`

