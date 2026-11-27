"""Person-4 join: aggregate image features, left-join onto reviews."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from statistics import mean

from app.io_jsonl import write_csv_from_models, write_jsonl
from app.paths import OUTPUT_CSV, OUTPUT_JSONL, OUTPUT_REPORT, ensure_dirs
from app.report import build_acceptance_report, write_acceptance_report
from app.schemas.models import (
    ImageFeatureRow,
    JoinResult,
    ReviewFeaturesRow,
    ReviewRow,
    TextFeatureRow,
)
from app.validate import validate_handoffs

REVIEW_FEATURE_FIELDS = [
    "review_id",
    "parent_asin",
    "split",
    "rating",
    "helpful_vote",
    "verified_purchase",
    "timestamp_ms",
    "image_count",
    "text_word_count",
    "sentiment_negative",
    "sentiment_neutral",
    "sentiment_positive",
    "usable_image_count",
    "image_status",
    "text_image_cosine_mean",
    "text_image_cosine_min",
    "text_run_id",
    "image_run_id",
]


def aggregate_images(
    reviews: list[ReviewRow],
    image_rows: list[ImageFeatureRow],
) -> dict[str, dict]:
    """Aggregate image features per review before joining.

    Mean/min use successful scores only. Failures stay null (never zero).
    Reviews with no attachments still inherit the batch image run_id when
    the image feature file uses a single run_id.
    """
    by_review: dict[str, list[ImageFeatureRow]] = defaultdict(list)
    for row in image_rows:
        by_review[row.review_id].append(row)

    batch_run_ids = {img.run_id for img in image_rows}
    batch_image_run_id = next(iter(batch_run_ids)) if len(batch_run_ids) == 1 else None

    agg: dict[str, dict] = {}
    for review in reviews:
        imgs = by_review.get(review.review_id, [])
        ok_scores = [
            img.text_image_cosine
            for img in imgs
            if img.status == "ok" and img.text_image_cosine is not None
        ]
        usable = len(ok_scores)
        # Prefer actual image rows when present (V2 model-ready may differ from attached count)
        total = len(imgs) if imgs else review.image_count

        if total == 0:
            image_status = "no_images"
        elif usable == 0:
            image_status = "failed"
        elif usable < total:
            image_status = "partial"
        else:
            image_status = "ok"

        run_ids = {img.run_id for img in imgs}
        if len(run_ids) == 1:
            image_run_id = next(iter(run_ids))
        elif len(run_ids) > 1:
            ordered = sorted(imgs, key=lambda i: i.image_index)
            image_run_id = ordered[0].run_id if ordered else batch_image_run_id
        else:
            image_run_id = batch_image_run_id

        agg[review.review_id] = {
            "usable_image_count": usable,
            "image_status": image_status,
            "text_image_cosine_mean": mean(ok_scores) if ok_scores else None,
            "text_image_cosine_min": min(ok_scores) if ok_scores else None,
            "image_run_id": image_run_id,
        }
    return agg


def join_features(
    reviews: list[ReviewRow],
    text_rows: list[TextFeatureRow],
    image_rows: list[ImageFeatureRow],
) -> list[ReviewFeaturesRow]:
    text_by_id = {t.review_id: t for t in text_rows}
    image_agg = aggregate_images(reviews, image_rows)

    joined: list[ReviewFeaturesRow] = []
    for review in reviews:
        text = text_by_id.get(review.review_id)
        img = image_agg[review.review_id]
        joined.append(
            ReviewFeaturesRow(
                review_id=review.review_id,
                parent_asin=review.parent_asin,
                split=review.split,
                rating=review.rating,
                helpful_vote=review.helpful_vote,
                verified_purchase=review.verified_purchase,
                timestamp_ms=review.timestamp_ms,
                image_count=review.image_count,
                text_word_count=text.text_word_count if text else None,
                sentiment_negative=text.sentiment_negative if text else None,
                sentiment_neutral=text.sentiment_neutral if text else None,
                sentiment_positive=text.sentiment_positive if text else None,
                usable_image_count=img["usable_image_count"],
                image_status=img["image_status"],
                text_image_cosine_mean=img["text_image_cosine_mean"],
                text_image_cosine_min=img["text_image_cosine_min"],
                text_run_id=text.run_id if text else None,
                image_run_id=img["image_run_id"],
            )
        )
    return joined


def run_join(
    reviews_path: Path,
    text_path: Path,
    images_path: Path,
    output_jsonl: Path = OUTPUT_JSONL,
    output_csv: Path = OUTPUT_CSV,
    report_path: Path = OUTPUT_REPORT,
) -> tuple[JoinResult, list[ReviewFeaturesRow]]:
    ensure_dirs()
    validation, reviews, text_rows, image_rows = validate_handoffs(
        reviews_path, text_path, images_path
    )

    if not validation.ok:
        acceptance = build_acceptance_report(
            validation=validation,
            joined=[],
            reviews=reviews,
            text_rows=text_rows,
            image_rows=image_rows,
            passed=False,
        )
        write_acceptance_report(report_path, acceptance)
        result = JoinResult(
            ok=False,
            row_count=0,
            output_jsonl=str(output_jsonl),
            output_csv=str(output_csv),
            report_path=str(report_path),
            validation=validation,
            acceptance=acceptance,
        )
        return result, []

    joined = join_features(reviews, text_rows, image_rows)
    write_jsonl(output_jsonl, joined)
    write_csv_from_models(output_csv, joined, REVIEW_FEATURE_FIELDS)

    acceptance = build_acceptance_report(
        validation=validation,
        joined=joined,
        reviews=reviews,
        text_rows=text_rows,
        image_rows=image_rows,
        passed=True,
    )
    write_acceptance_report(report_path, acceptance)

    result = JoinResult(
        ok=True,
        row_count=len(joined),
        output_jsonl=str(output_jsonl),
        output_csv=str(output_csv),
        report_path=str(report_path),
        validation=validation,
        acceptance=acceptance,
    )
    return result, joined
