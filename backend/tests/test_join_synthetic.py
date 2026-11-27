"""Golden test: synthetic 01+02+03 reproduce research_contract 04."""

from __future__ import annotations

import json
from pathlib import Path

from app.io_jsonl import load_jsonl
from app.join import join_features, run_join
from app.paths import SYNTHETIC_FILES
from app.schemas.models import ImageFeatureRow, ReviewFeaturesRow, ReviewRow, TextFeatureRow

FLOAT_TOL = 1e-9


def _approx_equal(a, b) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if isinstance(a, float) or isinstance(b, float):
        return abs(float(a) - float(b)) <= FLOAT_TOL
    return a == b


def test_synthetic_join_matches_golden(tmp_path: Path) -> None:
    out_jsonl = tmp_path / "04.jsonl"
    out_csv = tmp_path / "04.csv"
    report = tmp_path / "report.json"

    result, joined = run_join(
        SYNTHETIC_FILES["reviews"],
        SYNTHETIC_FILES["text"],
        SYNTHETIC_FILES["images"],
        output_jsonl=out_jsonl,
        output_csv=out_csv,
        report_path=report,
    )

    assert result.ok, result.validation.model_dump()
    assert result.row_count == 6

    expected, errs = load_jsonl(SYNTHETIC_FILES["joined"], ReviewFeaturesRow)
    assert not errs
    assert len(joined) == len(expected)

    for got, want in zip(joined, expected, strict=True):
        got_d = got.model_dump()
        want_d = want.model_dump()
        for key in want_d:
            assert _approx_equal(got_d[key], want_d[key]), (
                f"{got.review_id}.{key}: got {got_d[key]!r} want {want_d[key]!r}"
            )

    acceptance = json.loads(report.read_text(encoding="utf-8"))
    assert acceptance["passed"] is True


def test_join_features_edge_cases_inline() -> None:
    reviews, _ = load_jsonl(SYNTHETIC_FILES["reviews"], ReviewRow)
    text, _ = load_jsonl(SYNTHETIC_FILES["text"], TextFeatureRow)
    images, _ = load_jsonl(SYNTHETIC_FILES["images"], ImageFeatureRow)
    joined = join_features(reviews, text, images)
    by_id = {r.review_id: r for r in joined}

    assert by_id["syn_002"].image_status == "no_images"
    assert by_id["syn_002"].text_image_cosine_mean is None
    assert by_id["syn_004"].image_status == "failed"
    assert by_id["syn_004"].text_image_cosine_mean is None
    assert abs(by_id["syn_001"].text_image_cosine_mean - 0.295) < 1e-9
