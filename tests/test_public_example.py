from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from trait2gene.examples.public_schizophrenia import (
    compute_consistency_summary,
    compute_result_snapshot,
    write_public_schizophrenia_config,
)


def test_write_public_schizophrenia_config_uses_repo_local_paths(tmp_path: Path) -> None:
    config_path = write_public_schizophrenia_config(tmp_path)
    config_text = config_path.read_text(encoding="utf-8")

    assert str(tmp_path / "real_data" / "pops_upstream_example") in config_text
    assert str(tmp_path / "real_runs" / "schizophrenia_public_example" / "results") in config_text


def test_public_example_summaries(tmp_path: Path) -> None:
    ours_path = tmp_path / "ours.preds"
    upstream_path = tmp_path / "upstream.preds"
    results_dir = tmp_path / "results"
    tables_dir = results_dir / "tables"
    metadata_dir = results_dir / "metadata"
    tables_dir.mkdir(parents=True)
    metadata_dir.mkdir(parents=True)

    pd.DataFrame(
        {
            "ENSGID": ["ENSG0001", "ENSG0002"],
            "PoPS_Score": [1.0, 2.5],
        }
    ).to_csv(ours_path, sep="\t", index=False)
    pd.DataFrame(
        {
            "ENSGID": ["ENSG0001", "ENSG0002"],
            "PoPS_Score": [1.0, 2.0],
        }
    ).to_csv(upstream_path, sep="\t", index=False)

    pd.DataFrame(
        {
            "locus_id": ["locus_1", "locus_2"],
            "gene_symbol": ["GENE1", "GENE2"],
        }
    ).to_csv(tables_dir / "prioritized_genes.tsv", sep="\t", index=False)
    pd.DataFrame(
        {
            "gene_symbol": ["GENE1", "GENE2", "GENE3"],
            "rank": [1, 2, 3],
        }
    ).to_csv(tables_dir / "all_genes_ranked.tsv", sep="\t", index=False)
    pd.DataFrame(
        {
            "feature": ["feature_a", "feature_b"],
            "coefficient": [0.5, 0.2],
        }
    ).to_csv(tables_dir / "top_features.tsv", sep="\t", index=False)
    (metadata_dir / "run_metadata.json").write_text(
        json.dumps(
            {
                "stages": [
                    {"stage": "validate", "duration_seconds": 0.1},
                    {"stage": "pops", "duration_seconds": 3.5},
                ]
            }
        ),
        encoding="utf-8",
    )

    consistency = compute_consistency_summary(ours_path, upstream_path)
    snapshot = compute_result_snapshot(results_dir)

    assert consistency["n_genes_compared"] == 2
    assert consistency["max_abs_diff"] == 0.5
    assert snapshot["counts"] == {
        "prioritized_genes": 2,
        "all_ranked_genes": 3,
        "top_features": 2,
    }
    assert snapshot["top_prioritized_genes"][0] == {"locus_id": "locus_1", "gene_symbol": "GENE1"}
    assert snapshot["top_feature_names"] == ["feature_a", "feature_b"]
    assert snapshot["stage_durations_seconds"] == {"validate": 0.1, "pops": 3.5}
