"""Per-file and cross-file acceptance checks for teammate handoffs."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from app.io_jsonl import load_jsonl
from app.schemas.models import (
    ImageFeatureRow,
    ReviewRow,
    TextFeatureRow,
    ValidationIssue,
    ValidationReport,
)

PROB_SUM_TOL = 1e-5


def _issue(
    file: str,
    level: str,
    message: str,
    review_id: str | None = None,
    image_id: str | None = None,
) -> ValidationIssue:
    return ValidationIssue(
        file=file,
        level=level,  # type: ignore[arg-type]
        message=message,
        review_id=review_id,
        image_id=image_id,
    )


def validate_reviews(rows: list[ReviewRow], parse_errors: list[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for err in parse_errors:
        issues.append(_issue("01_reviews", "error", err))

    seen: set[str] = set()
    for row in rows:
        if row.review_id in seen:
            issues.append(
                _issue(
                    "01_reviews",
                    "error",
                    f"Duplicate review_id '{row.review_id}'",
                    row.review_id,
                )
            )
        seen.add(row.review_id)

    asin_splits: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        asin_splits[row.parent_asin].add(row.split)
    for asin, splits in asin_splits.items():
        if len(splits) > 1:
            issues.append(
                _issue(
                    "01_reviews",
                    "error",
                    f"parent_asin '{asin}' spans multiple splits: {sorted(splits)}",
                )
            )
    return issues


def validate_text(
    rows: list[TextFeatureRow],
    parse_errors: list[str],
    review_ids: set[str],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for err in parse_errors:
        issues.append(_issue("02_text_features", "error", err))

    seen: set[str] = set()
    for row in rows:
        if row.review_id in seen:
            issues.append(
                _issue(
                    "02_text_features",
                    "error",
                    f"Duplicate review_id '{row.review_id}'",
                    row.review_id,
                )
            )
        seen.add(row.review_id)

        if review_ids and row.review_id not in review_ids:
            issues.append(
                _issue(
                    "02_text_features",
                    "error",
                    f"review_id '{row.review_id}' not present in 01_reviews",
                    row.review_id,
                )
            )

        probs = [row.sentiment_negative, row.sentiment_neutral, row.sentiment_positive]
        if row.status == "ok":
            if any(p is None for p in probs):
                issues.append(
                    _issue(
                        "02_text_features",
                        "error",
                        "status=ok requires non-null sentiment probabilities",
                        row.review_id,
                    )
                )
            elif any(p is not None and (p < 0 or p > 1) for p in probs):
                issues.append(
                    _issue(
                        "02_text_features",
                        "error",
                        "sentiment probabilities must be in [0,1]",
                        row.review_id,
                    )
                )
            else:
                total = sum(p for p in probs if p is not None)
                if abs(total - 1.0) > PROB_SUM_TOL:
                    issues.append(
                        _issue(
                            "02_text_features",
                            "error",
                            f"sentiment probabilities sum to {total}, expected ~1.0",
                            row.review_id,
                        )
                    )
        else:
            if any(p is not None for p in probs):
                issues.append(
                    _issue(
                        "02_text_features",
                        "warning",
                        f"status={row.status} usually has null probabilities",
                        row.review_id,
                    )
                )

    if review_ids:
        missing = review_ids - seen
        for rid in sorted(missing):
            issues.append(
                _issue(
                    "02_text_features",
                    "error",
                    f"Missing text feature row for review_id '{rid}'",
                    rid,
                )
            )
    return issues


def validate_images(
    rows: list[ImageFeatureRow],
    parse_errors: list[str],
    reviews: list[ReviewRow],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for err in parse_errors:
        issues.append(_issue("03_image_features", "error", err))

    review_by_id = {r.review_id: r for r in reviews}
    review_ids = set(review_by_id)
    seen_image_ids: set[str] = set()
    images_by_review: dict[str, list[ImageFeatureRow]] = defaultdict(list)

    for row in rows:
        if row.image_id in seen_image_ids:
            issues.append(
                _issue(
                    "03_image_features",
                    "error",
                    f"Duplicate image_id '{row.image_id}'",
                    row.review_id,
                    row.image_id,
                )
            )
        seen_image_ids.add(row.image_id)
        images_by_review[row.review_id].append(row)

        if review_ids and row.review_id not in review_ids:
            issues.append(
                _issue(
                    "03_image_features",
                    "error",
                    f"review_id '{row.review_id}' not present in 01_reviews",
                    row.review_id,
                    row.image_id,
                )
            )
            continue

        if row.status == "ok":
            if row.text_image_cosine is None:
                issues.append(
                    _issue(
                        "03_image_features",
                        "error",
                        "status=ok requires non-null text_image_cosine",
                        row.review_id,
                        row.image_id,
                    )
                )
            elif not (-1.0 <= row.text_image_cosine <= 1.0):
                issues.append(
                    _issue(
                        "03_image_features",
                        "error",
                        f"text_image_cosine {row.text_image_cosine} outside [-1,1]",
                        row.review_id,
                        row.image_id,
                    )
                )
        else:
            if row.text_image_cosine is not None:
                issues.append(
                    _issue(
                        "03_image_features",
                        "error",
                        f"status={row.status} must keep text_image_cosine null "
                        "(do not use 0 for failure)",
                        row.review_id,
                        row.image_id,
                    )
                )

    for review in reviews:
        imgs = images_by_review.get(review.review_id, [])
        if review.image_count == 0 and imgs:
            issues.append(
                _issue(
                    "03_image_features",
                    "error",
                    f"image_count=0 but {len(imgs)} image row(s) present "
                    "(no image rows for reviews with no attachments)",
                    review.review_id,
                )
            )
        if review.image_count > 0 and not imgs:
            issues.append(
                _issue(
                    "03_image_features",
                    "error",
                    f"image_count={review.image_count} but no image feature rows",
                    review.review_id,
                )
            )
        if review.image_count > 0 and imgs and len(imgs) != review.image_count:
            # Person 3 V2 uses model-ready subset; warn rather than hard-fail if counts differ
            issues.append(
                _issue(
                    "03_image_features",
                    "warning",
                    f"image_count={review.image_count} but found {len(imgs)} image row(s); "
                    "confirm whether image_count is attached photos or model-ready images",
                    review.review_id,
                )
            )

        indexes = sorted(i.image_index for i in imgs)
        if indexes and indexes != list(range(len(indexes))):
            issues.append(
                _issue(
                    "03_image_features",
                    "warning",
                    f"image_index values {indexes} are not contiguous zero-based",
                    review.review_id,
                )
            )

    return issues


def validate_handoffs(
    reviews_path: Path,
    text_path: Path,
    images_path: Path,
) -> tuple[
    ValidationReport,
    list[ReviewRow],
    list[TextFeatureRow],
    list[ImageFeatureRow],
]:
    reviews, review_errs = load_jsonl(reviews_path, ReviewRow)
    text_rows, text_errs = load_jsonl(text_path, TextFeatureRow)
    image_rows, image_errs = load_jsonl(images_path, ImageFeatureRow)

    issues: list[ValidationIssue] = []
    issues.extend(validate_reviews(reviews, review_errs))
    review_ids = {r.review_id for r in reviews}
    issues.extend(validate_text(text_rows, text_errs, review_ids))
    issues.extend(validate_images(image_rows, image_errs, reviews))

    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]
    report = ValidationReport(
        ok=len(errors) == 0 and len(reviews) > 0,
        errors=errors,
        warnings=warnings,
        counts={
            "reviews": len(reviews),
            "text_features": len(text_rows),
            "image_features": len(image_rows),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    )
    return report, reviews, text_rows, image_rows
