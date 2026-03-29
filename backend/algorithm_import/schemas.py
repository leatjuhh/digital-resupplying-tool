from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ArtifactLineage(BaseModel):
    source_path: str
    size_bytes: int
    modified_at: str | None = None
    sha256: str


class ExternalAlgorithmWeekSummary(BaseModel):
    year: int
    week: int
    proposal_count: int
    observed_move_count: int
    model_opportunity_count: int
    overlap_move_count: int
    observed_opportunity_recall: float
    model_overlap_ratio: float
    lineage: ArtifactLineage | None = None


class ExternalAlgorithmModelSummary(BaseModel):
    data_available: bool
    average_precision_test: float | None = None
    top_k_recall_test: float | None = None
    top_k_precision_test: float | None = None
    binary_precision_test: float | None = None
    binary_recall_test: float | None = None
    feature_importance: list[dict[str, Any]] = Field(default_factory=list)
    lineage: ArtifactLineage | None = None


class ExternalAlgorithmDatasetStatus(BaseModel):
    data_available: bool
    assist_mode: str
    dataset_root: str
    latest_year: int | None = None
    latest_week: int | None = None
    processed_week_count: int = 0
    weeks_available: list[ExternalAlgorithmWeekSummary] = Field(default_factory=list)
    aggregate_training_summary: dict[str, Any] | None = None
    aggregate_model_summary: ExternalAlgorithmModelSummary
    refresh_state_lineage: ArtifactLineage | None = None
    errors: list[str] = Field(default_factory=list)
