# trait2gene

`trait2gene` is an end-to-end PoPS-oriented CLI that hides resource resolution,
MAGMA handoff, feature preparation, PoPS execution, locus prioritization, and
reporting behind a single workflow.

MAGMA stays external and is not redistributed. The package vendors the upstream
PoPS Python scripts for compatibility, while `trait2gene` owns the config
contract, stage orchestration, standardized outputs, and downstream reporting.

## Licensing

Because the package vendors GPL-licensed upstream PoPS code, the combined
distribution is shipped under GPL-3.0. MAGMA itself is still treated as an
external dependency and is not bundled.

## Install

```bash
pip install -e .[dev]
```

To build the Sphinx documentation:

```bash
pip install -e .[docs]
python scripts/build_sphinx_docs.py
```

## Quickstart

```bash
trait2gene validate src/trait2gene/data/examples/config.minimal.yaml
trait2gene fetch-resources src/trait2gene/data/examples/config.minimal.yaml
```

Real-path templates for actual runs:

- `src/trait2gene/data/examples/config.realpaths.template.yaml`
- `src/trait2gene/data/examples/config.precomputed.template.yaml`

Tutorials:

- `docs/source/tutorials/real-paths.md`
- `docs/source/tutorials/public-schizophrenia.md`
- generated Sphinx site under `docs/build/html/`
- published docs index: `https://dai540.github.io/trait2gene/`

Real public example:

```bash
python scripts/run_public_schizophrenia_example.py
```

This one-shot command prepares public inputs, generates a machine-local config,
runs the pipeline, and writes:

- `real_runs/schizophrenia_public_example/results/reports/report.html`
- `real_runs/schizophrenia_public_example/verification_summary.json`
- `real_runs/schizophrenia_public_example/result_snapshot.json`

## Documentation

The documentation source lives under `docs/source/` and is built with Sphinx.
The published documentation homepage is
[`index.html`](https://dai540.github.io/trait2gene/).

Common commands:

```bash
python scripts/build_sphinx_docs.py
python -m sphinx -b html docs/source docs/build/html
```

## Commands

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

## Notes

- Default PoPS analysis settings track the upstream defaults:
  `ridge`, MAGMA covariates on, MAGMA error covariance on, HLA removal on.
- `standard` mode expects a pre-munged feature bundle and an external MAGMA binary.
- `advanced` mode is reserved for custom resources and raw feature preparation.
- `prep-features` can either copy a pre-munged prefix into standardized outputs or
  run the vendored `munge_feature_directory.py` on raw features.
- `run-pops` executes the vendored upstream `pops.py` against standardized
  `work/magma/` and `work/features/` artifacts.
