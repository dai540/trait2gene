from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ConfigBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class InputConfig(ConfigBase):
    sumstats: Path
    genome_build: Literal["GRCh37", "GRCh38"]
    ancestry: Literal["EUR", "AFR", "EAS", "SAS", "AMR"]


class ColumnsConfig(ConfigBase):
    snp: str = "SNP"
    p: str = "P"
    n: str | None = "N"
    chr: str | None = "CHR"
    bp: str | None = "BP"
    a1: str | None = "A1"
    a2: str | None = "A2"


class SampleSizeConfig(ConfigBase):
    mode: Literal["column", "fixed"] = "column"
    value: str | int = "N"


class ResourcesConfig(ConfigBase):
    magma_bin: str | Path = "auto"
    reference_panel: str | Path = "auto"
    gene_locations: str | Path = "auto"
    gene_annotation: str | Path = "auto"
    feature_bundle: str = "default_full_v1"
    feature_matrix_prefix: str | Path | None = None
    raw_feature_dir: Path | None = None
    control_features_path: str | Path | None = None
    subset_features_path: str | Path | None = None
    precomputed_magma_prefix: str | Path | None = None


class MagmaConfig(ConfigBase):
    model: str = "snp-wise=mean"
    annotation_snp_loc_source: Literal["reference_bim", "sumstats"] = "reference_bim"


class FeaturePrepConfig(ConfigBase):
    nan_policy: Literal["raise", "ignore", "mean", "zero"] = "raise"
    max_cols: int = Field(default=5000, ge=1)


class PopsConfig(ConfigBase):
    method: Literal["ridge", "lasso", "linreg"] = "ridge"
    use_magma_covariates: bool = True
    use_magma_error_cov: bool = True
    remove_hla: bool = True
    project_out_covariates_chromosomes: list[str] | None = None
    feature_selection_chromosomes: list[str] | None = None
    training_chromosomes: list[str] | None = None
    feature_selection_p_cutoff: float = 0.05
    feature_selection_max_num: int | None = None
    feature_selection_fss_num_features: int | None = None
    save_matrix_files: bool = False
    random_seed: int = 42
    verbose: bool = False
    y_path: Path | None = None
    y_covariates_path: Path | None = None
    y_error_cov_path: Path | None = None


class PrioritizationConfig(ConfigBase):
    mode: Literal["lead_snp_window", "locus_file"] = "lead_snp_window"
    window_bp: int = Field(default=500_000, ge=1)
    locus_file: Path | None = None


class AnalysisConfig(ConfigBase):
    magma: MagmaConfig = Field(default_factory=MagmaConfig)
    feature_prep: FeaturePrepConfig = Field(default_factory=FeaturePrepConfig)
    pops: PopsConfig = Field(default_factory=PopsConfig)
    prioritization: PrioritizationConfig = Field(default_factory=PrioritizationConfig)


class OutputConfig(ConfigBase):
    outdir: Path
    write_html_report: bool = True
    write_json_summary: bool = True
    overwrite: bool = True


class AppConfig(ConfigBase):
    mode: Literal["standard", "advanced"] = "standard"
    project: str
    trait: str
    input: InputConfig
    columns: ColumnsConfig = Field(default_factory=ColumnsConfig)
    sample_size: SampleSizeConfig = Field(default_factory=SampleSizeConfig)
    resources: ResourcesConfig = Field(default_factory=ResourcesConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    output: OutputConfig
