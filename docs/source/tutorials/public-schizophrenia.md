# Tutorial: Public Schizophrenia Example

This article documents a real `trait2gene` analysis run using public data:

- the public PoPS schizophrenia example data from the FinucaneLab repository
- a schizophrenia association table downloaded from the GWAS Catalog API
- a locus file derived from public MAGMA gene-level output

The goal is not to rerun MAGMA locally. MAGMA was not installed in this
environment, so the run uses public precomputed MAGMA outputs and still
executes the rest of the `trait2gene` pipeline for real.

## Data sources

- PoPS upstream example repository:
  `https://github.com/FinucaneLab/pops`
- GWAS Catalog schizophrenia associations API:
  `https://www.ebi.ac.uk/gwas/rest/api/v2/associations?efo_id=MONDO_0005090&page=0&size=200`

## Files used in this run

- `real_runs/schizophrenia_public_example/config.yaml`
- `scripts/prepare_public_schizophrenia_example.py`
- `scripts/run_public_schizophrenia_example.py`
- `real_runs/schizophrenia_public_example/schizophrenia_gwascatalog_hits.tsv`
- `real_runs/schizophrenia_public_example/schizophrenia_magma_top_loci.tsv`
- `real_runs/schizophrenia_public_example/verification_summary.json`
- `real_runs/schizophrenia_public_example/result_snapshot.json`

## One-shot reproduction

```bash
python scripts/run_public_schizophrenia_example.py
```

This command:

- clones the public `FinucaneLab/pops` example repository into `real_data/`
- downloads 200 schizophrenia associations from the GWAS Catalog API
- derives 8 non-overlapping loci from strong non-HLA MAGMA hits
- generates `real_runs/schizophrenia_public_example/config.yaml`
- runs the full `trait2gene` pipeline
- writes verification and snapshot JSON sidecars

## Manual step-by-step reproduction

```bash
python scripts/prepare_public_schizophrenia_example.py
trait2gene validate real_runs/schizophrenia_public_example/config.yaml
trait2gene doctor --config real_runs/schizophrenia_public_example/config.yaml
trait2gene run real_runs/schizophrenia_public_example/config.yaml
```

`validate` passes cleanly in this mode because the public example uses
`resources.precomputed_magma_prefix` instead of requiring a local MAGMA binary.

## What the pipeline did

1. validated the config and downloaded public inputs
2. wrote the resolved manifest and software metadata
3. copied public `PASS_Schizophrenia.genes.out` and `.genes.raw` into `work/magma/`
4. ran vendored `munge_feature_directory.py` on the public raw feature files
5. ran vendored upstream `pops.py`
6. prioritized genes within 8 loci
7. wrote HTML, JSON, TSV, and metadata outputs

## Output locations

The run outputs live under:

- `real_runs/schizophrenia_public_example/results`

Important outputs:

- `work/pops/schizophrenia.preds`
- `work/pops/schizophrenia.coefs`
- `work/pops/schizophrenia.marginals`
- `tables/prioritized_genes.tsv`
- `tables/all_genes_ranked.tsv`
- `tables/top_features.tsv`
- `reports/report.html`
- `metadata/run_metadata.json`

## Runtime summary

From `result_snapshot.json` and `metadata/run_metadata.json`:

- total status: `ok`
- `feature_prep`: about 2.51 seconds
- `pops`: about 60.57 seconds
- whole pipeline: about 63.47 seconds

## Result snapshot

The run produced:

- 8 prioritized genes
- 103 ranked genes across the selected loci
- 20 top features in the summary table

Top prioritized genes:

| Locus | Top gene |
| --- | --- |
| `magma_top_01` | `GBF1` |
| `magma_top_02` | `CACNA1C` |
| `magma_top_03` | `TCF4` |
| `magma_top_04` | `IREB2` |
| `magma_top_05` | `PPP1R16B` |
| `magma_top_06` | `PTBP2` |
| `magma_top_07` | `TNRC6B` |
| `magma_top_08` | `KLC1` |

Top feature names started with:

- `GTEx.53`
- `mouse_brain2_projected_pcaloadings_clusters.59`
- `mouse_brain2_projected_pcaloadings_clusters.25`
- `mouse_brain2_projected_pcaloadings.84`
- `mouse_brain2_projected_pcaloadings_clusters.74`

## Consistency check against upstream PoPS output

As a sanity check, the `trait2gene` PoPS score output was compared with the
public upstream example output:

- compared genes: `18,383`
- Pearson correlation: `~1.0`
- maximum absolute score difference: `2.47e-14`
- mean absolute score difference: `2.73e-15`

That means the wrapped `trait2gene` execution reproduced the public upstream
PoPS example essentially exactly while still producing standardized downstream
artifacts and reports.

## Why this tutorial uses `locus_file`

The public PoPS example repository ships:

- raw features
- pre-munged features
- precomputed MAGMA gene outputs

It does not ship the original SNP-level summary statistics used to generate
those MAGMA outputs. For that reason:

- a real schizophrenia association table from GWAS Catalog was downloaded as the config input
- locus prioritization used a locus file derived from the public MAGMA results

