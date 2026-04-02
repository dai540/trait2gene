PIPELINE_STEPS = [
    "validate",
    "resolve-resources",
    "run-magma",
    "prep-features",
    "run-pops",
    "prioritize",
    "report",
]

DEFAULT_CACHE_APPNAME = "trait2gene"
DEFAULT_FEATURE_BUNDLE = "default_full_v1"
DEFAULT_LICENSE_NOTE = "external binary; not redistributed"
DEFAULT_WINDOW_BP = 500_000
DEFAULT_FEATURE_PREFIX_BASENAME = "pops_features"
MAGMA_REFERENCE_SUFFIXES = (".bed", ".bim", ".fam")
MAGMA_GENE_OUTPUT_SUFFIXES = (".genes.out", ".genes.raw")

OUTPUT_LAYOUT = {
    "qc": "qc",
    "normalized": "work/normalized",
    "magma": "work/magma",
    "features": "work/features",
    "pops": "work/pops",
    "tables": "tables",
    "reports": "reports",
    "metadata": "metadata",
}

AUTO_REFERENCE_PANELS = {
    "GRCh37": {
        "EUR": "1000G_Phase3_EUR",
        "AFR": "1000G_Phase3_AFR",
        "EAS": "1000G_Phase3_EAS",
        "SAS": "1000G_Phase3_SAS",
        "AMR": "1000G_Phase3_AMR",
    },
    "GRCh38": {
        "EUR": "1000G_Phase3_GRCh38_EUR",
        "AFR": "1000G_Phase3_GRCh38_AFR",
        "EAS": "1000G_Phase3_GRCh38_EAS",
        "SAS": "1000G_Phase3_GRCh38_SAS",
        "AMR": "1000G_Phase3_GRCh38_AMR",
    },
}

HLA_REGIONS = {
    "GRCh37": ("6", 25_000_000, 34_000_000),
    "GRCh38": ("6", 28_510_120, 33_480_577),
}
