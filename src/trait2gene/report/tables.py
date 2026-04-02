from __future__ import annotations

from pathlib import Path

import pandas as pd

from trait2gene.domain.genes import detect_column


def top_features_frame(coefs_path: Path | None, *, limit: int = 20) -> pd.DataFrame:
    if coefs_path is None or not coefs_path.exists():
        return pd.DataFrame(columns=["feature", "coefficient", "abs_coefficient"])

    frame = pd.read_csv(coefs_path, sep=None, engine="python")
    feature_column = detect_column(
        frame.columns,
        ["feature", "Feature", "covariate", "name", "parameter"],
        required=False,
    )
    coefficient_column = detect_column(
        frame.columns,
        ["coef", "coefficient", "beta", "weight"],
        required=False,
    )
    if not feature_column or not coefficient_column:
        return pd.DataFrame(columns=["feature", "coefficient", "abs_coefficient"])

    result = pd.DataFrame(
        {
            "feature": frame[feature_column].astype(str),
            "coefficient": pd.to_numeric(frame[coefficient_column], errors="coerce"),
        }
    ).dropna(subset=["coefficient"])
    result = result[~result["feature"].isin({"METHOD", "SELECTED_CV_ALPHA", "BEST_CV_SCORE"})].copy()
    result["abs_coefficient"] = result["coefficient"].abs()
    return result.sort_values("abs_coefficient", ascending=False).head(limit)
