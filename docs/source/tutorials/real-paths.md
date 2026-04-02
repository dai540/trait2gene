# Tutorial: Real Paths and End-to-End Runs

This walkthrough shows how to run `trait2gene` with real filesystem paths
instead of `auto`, so the pipeline can execute without extra path guessing.

## Two common patterns

## 1. Full run with external MAGMA and pre-munged features

Use this when `trait2gene run` should execute MAGMA itself and you already have
a PoPS-ready feature prefix.

Start from:

- `src/trait2gene/data/examples/config.realpaths.template.yaml`

The fields that usually need real absolute paths are:

- `input.sumstats`
- `resources.magma_bin`
- `resources.reference_panel`
- `resources.gene_locations`
- `resources.gene_annotation`
- `resources.feature_matrix_prefix`
- `resources.control_features_path`
- `output.outdir`

Minimal example:

```yaml
project: bmi_realpaths
trait: bmi

input:
  sumstats: /data/gwas/bmi/bmi.sumstats.tsv.gz
  genome_build: GRCh37
  ancestry: EAS

resources:
  magma_bin: /opt/magma/magma
  reference_panel: /data/reference/1000g/eas/g1000_eas
  gene_locations: /data/reference/magma/gene_loc_build37.txt
  gene_annotation: /data/reference/pops/gene_annot.tsv
  feature_matrix_prefix: /data/reference/pops/features/default_full_v1/pops_features
  control_features_path: /data/reference/pops/features/features_jul17_control.txt

output:
  outdir: /data/projects/trait2gene/results/bmi_realpaths
```

Run order:

```bash
trait2gene validate config.yaml
trait2gene doctor --config config.yaml
trait2gene run config.yaml
```

## 2. Reuse precomputed MAGMA and pre-munged features

Use this when MAGMA has already been run elsewhere and you only want PoPS,
locus prioritization, and reporting.

Start from:

- `src/trait2gene/data/examples/config.precomputed.template.yaml`

Key path fields:

- `resources.precomputed_magma_prefix`
- `resources.gene_annotation`
- `resources.feature_matrix_prefix`
- `resources.control_features_path`
- `analysis.prioritization.locus_file`
- `output.outdir`

Example commands:

```bash
trait2gene validate config.precomputed.yaml
trait2gene run-pops config.precomputed.yaml
trait2gene prioritize config.precomputed.yaml
trait2gene report config.precomputed.yaml
```

## What each path must point to

### `resources.reference_panel`

This is a PLINK prefix, not a directory. If the prefix is
`/data/reference/1000g/eas/g1000_eas`, then these files must exist:

- `/data/reference/1000g/eas/g1000_eas.bed`
- `/data/reference/1000g/eas/g1000_eas.bim`
- `/data/reference/1000g/eas/g1000_eas.fam`

### `resources.precomputed_magma_prefix`

This is also a prefix. If it is `/data/projects/cad/magma/cad`, then these
files must exist:

- `/data/projects/cad/magma/cad.genes.out`
- `/data/projects/cad/magma/cad.genes.raw`

### `resources.feature_matrix_prefix`

This is the prefix written by `munge_feature_directory.py`. If it is
`/data/reference/pops/features/default_full_v1/pops_features`, then there
should be:

- `pops_features.rows.txt`
- `pops_features.cols.0.txt`, `pops_features.cols.1.txt`, ...
- `pops_features.mat.0.npy`, `pops_features.mat.1.npy`, ...

### `resources.raw_feature_dir`

This should be a directory of tab-separated feature files. Each file must:

- have a header
- use `ENSGID` as the first column
- have unique feature names across all files

If you set `resources.raw_feature_dir`, `trait2gene prep-features` runs the
vendored upstream munging script and copies the resulting prefix into
`work/features/pops_features`.

## Recommended validation sequence

Before a full run:

```bash
trait2gene validate config.yaml
trait2gene doctor --config config.yaml
trait2gene fetch-resources config.yaml
trait2gene inspect outputs /data/projects/trait2gene/results/bmi_realpaths
```

## Standard outputs after success

- `work/magma/*.genes.out` and `*.genes.raw`
- `work/features/pops_features.*`
- `work/pops/*.preds`, `*.coefs`, `*.marginals`
- `tables/prioritized_genes.tsv`
- `tables/all_genes_ranked.tsv`
- `reports/report.html`
- `reports/summary.json`
- `metadata/run_metadata.json`

## Troubleshooting

### Validation says a prefix is unresolved

Usually the path points to the right directory but the wrong prefix basename.
Check whether you supplied the full prefix and not only the parent directory.

### `run-magma` fails even though MAGMA exists

Check:

- `resources.magma_bin` is executable
- `resources.reference_panel` points to a PLINK prefix
- `resources.gene_locations` matches the same genome build as your summary statistics

### `run-pops` fails after feature preparation

Check:

- `resources.gene_annotation` contains `ENSGID`, `CHR`, and `TSS`
- `work/features/pops_features.rows.txt` exists
- `work/magma/<trait>.genes.out` and `.genes.raw` exist

