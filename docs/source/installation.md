# Installation

## Runtime install

Install the package in editable mode for development:

```bash
pip install -e .[dev]
```

This installs the Python package and CLI entry point:

```bash
trait2gene --help
```

## Documentation install

To build the Sphinx documentation locally:

```bash
pip install -e .[docs]
python scripts/build_sphinx_docs.py
```

Generated HTML is written to:

- `docs/build/html`

## External dependencies

`trait2gene` treats MAGMA as an external binary. It is not redistributed in the
Python package. Depending on your run mode, you may also need local access to:

- a PLINK reference panel prefix
- a MAGMA gene location file
- a PoPS gene annotation table
- a pre-munged PoPS feature prefix or a raw feature directory

## Public example without local MAGMA

The public schizophrenia tutorial uses:

- `resources.precomputed_magma_prefix`
- public raw feature files

That means you can run the end-to-end example without a local MAGMA install:

```bash
python scripts/run_public_schizophrenia_example.py
```

