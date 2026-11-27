"""Smoke-check the uploaded Person-2 text features file."""

from __future__ import annotations

from pathlib import Path

from app.io_jsonl import load_jsonl
from app.schemas.models import TextFeatureRow
from app.validate import validate_text

TEXT_PATH = (
    Path(__file__).resolve().parent.parent
    / "examples"
    / "person2_text_features_image_v2_test.jsonl"
)


def test_uploaded_text_features_schema() -> None:
    assert TEXT_PATH.exists(), f"missing {TEXT_PATH}"
    rows, errs = load_jsonl(TEXT_PATH, TextFeatureRow)
    assert not errs
    assert len(rows) == 100
    # Validate text alone (empty review_ids set skips cross-file presence checks)
    issues = validate_text(rows, [], set())
    errors = [i for i in issues if i.level == "error"]
    assert not errors, errors[:5]
