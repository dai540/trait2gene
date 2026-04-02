from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MagmaManifest(SchemaBase):
    binary: str
    version: str | None = None
    source: str
    license_note: str
    precomputed_prefix: str | None = None
    status: Literal["resolved", "unresolved"]


class ReferenceManifest(SchemaBase):
    panel: str
    build: str
    path_prefix: str
    source_url: str | None = None
    status: Literal["resolved", "unresolved"]


class GeneLocationsManifest(SchemaBase):
    build: str
    path: str
    status: Literal["resolved", "unresolved"]


class GeneAnnotationManifest(SchemaBase):
    name: str
    path: str
    status: Literal["resolved", "unresolved"]


class FeaturesManifest(SchemaBase):
    bundle: str
    format: Literal["pre_munged", "raw", "unknown"]
    prefix: str
    num_feature_chunks: int
    source: str
    raw_dir: str | None = None
    status: Literal["resolved", "unresolved"]


class ResolvedManifest(SchemaBase):
    magma: MagmaManifest
    reference: ReferenceManifest
    gene_locations: GeneLocationsManifest
    gene_annotation: GeneAnnotationManifest
    features: FeaturesManifest
