"""Human-readable acceptance reports for Person-4 handoffs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.schemas.models import (
    ImageFeatureRow,
    ReviewFeaturesRow,
    ReviewRow,
    TextFeatureRow,
    ValidationReport,
)


def build_acceptance_report(
    *,
    validation: ValidationReport,
    joined: list[ReviewFeaturesRow],
    reviews: list[ReviewRow],
    text_rows: list[TextFeatureRow],
    image_rows: list[ImageFeatureRow],
    passed: bool,
) -> dict:
    review_ids = [r.review_id for r in reviews]
    joined_ids = [r.review_id for r in joined]

    image_status_counts: dict[str, int] = {}
    for row in joined:
        image_status_counts[row.image_status] = image_status_counts.get(row.image_status, 0) + 1

    checks = {
        "review_ids_unique": len(review_ids) == len(set(review_ids)),
        "text_ids_unique": len({t.review_id for t in text_rows}) == len(text_rows),
        "image_ids_unique": len({i.image_id for i in image_rows}) == len(image_rows),
        "final_row_count_matches_reviews": len(joined) == len(reviews) if passed else False,
        "final_review_ids_match": joined_ids == review_ids if passed else False,
        "no_parent_asin_split_leak": validation.ok
        or not any("spans multiple splits" in e.message for e in validation.errors),
        "validation_ok": validation.ok,
    }

    return {
        "passed": passed and all(checks.values()),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "reviews": len(reviews),
            "text_features": len(text_rows),
            "image_features": len(image_rows),
            "joined_rows": len(joined),
            "image_status": image_status_counts,
        },
        "checks": checks,
        "validation_errors": [e.model_dump() for e in validation.errors],
        "validation_warnings": [w.model_dump() for w in validation.warnings],
        "notes": [
            "JSON null means unavailable; 0 remains a valid observation.",
            "Mean/min cosine use successful image scores only.",
            "Failure must never become score zero.",
            "Synthetic or unvalidated scores must not enter research results.",
        ],
    }


def write_acceptance_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def format_validation_summary(validation: ValidationReport) -> str:
    lines = [
        f"Validation: {'PASS' if validation.ok else 'FAIL'}",
        f"  reviews={validation.counts.get('reviews', 0)} "
        f"text={validation.counts.get('text_features', 0)} "
        f"images={validation.counts.get('image_features', 0)}",
    ]
    for err in validation.errors[:50]:
        rid = f" [{err.review_id}]" if err.review_id else ""
        lines.append(f"  ERROR {err.file}{rid}: {err.message}")
    if len(validation.errors) > 50:
        lines.append(f"  ... and {len(validation.errors) - 50} more errors")
    for warn in validation.warnings[:20]:
        rid = f" [{warn.review_id}]" if warn.review_id else ""
        lines.append(f"  WARN  {warn.file}{rid}: {warn.message}")
    if not validation.errors and not validation.warnings:
        lines.append("  No issues.")
    return "\n".join(lines)
