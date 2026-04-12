# Tutorial: External Tools Dry Run

This tutorial is for a real project that will eventually use external MAGMA or
feature resources, but where repository size must stay small.

## Strategy

- keep the package repository empty of downloaded data
- point the config at local external paths
- use `trait2gene validate`
- use `trait2gene plan`
- materialize only metadata and reports with `trait2gene run`

## Example resource block

```toml
[resources]
precomputed_magma_prefix = "/data/magma/trait"
feature_prefix = "/data/features/pops_features"
gene_annotation = "/data/reference/gene_annot.tsv"
```

This keeps the repository light while still giving the project a reproducible
configuration contract.

