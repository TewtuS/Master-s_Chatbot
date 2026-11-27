"""Pydantic models matching research_contract field definitions."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Split = Literal["train", "validation", "test"]
TextStatus = Literal["ok", "empty_text", "unsupported_language", "inference_failed"]
ImageStatusRow = Literal["ok", "download_failed", "decode_failed", "inference_failed"]
ImageStatusAgg = Literal["no_images", "failed", "partial", "ok"]
ImageSource = Literal["customer_review"]


class ReviewRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_id: str
    parent_asin: str
    rating: int = Field(ge=1, le=5)
    helpful_vote: int = Field(ge=0)
    verified_purchase: bool | None
    timestamp_ms: int
    image_count: int = Field(ge=0)
    review_text: str
    split: Split


class TextFeatureRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_id: str
    status: TextStatus
    sentiment_negative: float | None = None
    sentiment_neutral: float | None = None
    sentiment_positive: float | None = None
    text_word_count: int | None = None
    error_code: str | None = None
    run_id: str


class ImageFeatureRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_id: str
    image_id: str
    image_index: int = Field(ge=0)
    image_source: ImageSource = "customer_review"
    status: ImageStatusRow
    width_px: int | None = None
    height_px: int | None = None
    brightness_mean: float | None = None
    text_image_cosine: float | None = None
    error_code: str | None = None
    run_id: str


class ReviewFeaturesRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_id: str
    parent_asin: str
    split: Split
    rating: int
    helpful_vote: int
    verified_purchase: bool | None
    timestamp_ms: int
    image_count: int
    text_word_count: int | None
    sentiment_negative: float | None
    sentiment_neutral: float | None
    sentiment_positive: float | None
    usable_image_count: int
    image_status: ImageStatusAgg
    text_image_cosine_mean: float | None
    text_image_cosine_min: float | None
    text_run_id: str | None
    image_run_id: str | None


class ValidationIssue(BaseModel):
    file: str
    level: Literal["error", "warning"]
    message: str
    review_id: str | None = None
    image_id: str | None = None


class ValidationReport(BaseModel):
    ok: bool
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]
    counts: dict[str, int]


class JoinResult(BaseModel):
    ok: bool
    row_count: int
    output_jsonl: str
    output_csv: str
    report_path: str
    validation: ValidationReport
    acceptance: dict
