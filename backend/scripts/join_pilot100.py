#!/usr/bin/env python3
"""Join Pilot 100 image pack with Person-2 text features locally.

The Pilot zip does not include full 01_reviews (no rating/helpful_vote/parent_asin).
This produces a partial 04 table for the overlapping review_ids.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

import pandas as pd

BACKEND = Path(__file__).resolve().parent.parent
DEFAULT_TEXT = BACKEND / "examples" / "person2_text_features_image_v2_test.jsonl"
DEFAULT_PILOT = BACKEND.parent / "pilot100" / "Pilot 100 data"
DEFAULT_OUT = BACKEND / "outputs"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", type=Path, default=DEFAULT_TEXT)
    parser.add_argument("--pilot-dir", type=Path, default=DEFAULT_PILOT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    pilot = args.pilot_dir
    images_path = pilot / "image_features.jsonl"
    rif_path = pilot / "review_image_features.csv"
    ann_path = pilot / "manual_validation_sample_annotated.csv"

    for path in (args.text, images_path, rif_path):
        if not path.exists():
            print(f"Missing: {path}", file=sys.stderr)
            return 2

    text_rows = load_jsonl(args.text)
    images = load_jsonl(images_path)
    rif = pd.read_csv(rif_path)
    rif["review_id"] = rif["review_id"].astype(str)

    text_from_ann: dict[str, str] = {}
    if ann_path.exists():
        ann = pd.read_csv(ann_path)
        text_from_ann = (
            ann.groupby("review_id")["review_text"].first().astype(str).to_dict()
        )

    text_by = {t["review_id"]: t for t in text_rows}
    img_by: dict[str, list[dict]] = defaultdict(list)
    for img in images:
        img_by[img["review_id"]].append(img)

    rif_ids = set(rif["review_id"])
    text_ids = set(text_by)
    overlap = sorted(text_ids & rif_ids)
    rif_by = rif.set_index("review_id").to_dict("index")

    batch_run = {i.get("run_id") for i in images if i.get("run_id")}
    batch_image_run_id = next(iter(batch_run)) if len(batch_run) == 1 else None

    joined: list[dict] = []
    status_counts: Counter[str] = Counter()
    for rid in overlap:
        meta = rif_by[rid]
        text = text_by[rid]
        imgs = img_by.get(rid, [])
        ok_scores = [
            i["text_image_cosine"]
            for i in imgs
            if i.get("status") == "ok" and i.get("text_image_cosine") is not None
        ]
        usable = len(ok_scores)
        total = len(imgs) if imgs else int(meta.get("image_count") or 0)
        if total == 0:
            image_status = "no_images"
        elif usable == 0:
            image_status = "failed"
        elif usable < total:
            image_status = "partial"
        else:
            image_status = "ok"
        status_counts[image_status] += 1

        run_ids = {i.get("run_id") for i in imgs if i.get("run_id")}
        if len(run_ids) == 1:
            image_run_id = next(iter(run_ids))
        elif imgs:
            image_run_id = sorted(imgs, key=lambda x: x.get("image_index", 0))[0].get(
                "run_id"
            )
        else:
            image_run_id = batch_image_run_id

        joined.append(
            {
                "review_id": rid,
                "parent_asin": None,
                "split": meta["split"],
                "rating": None,
                "helpful_vote": None,
                "verified_purchase": None,
                "timestamp_ms": None,
                "image_count": int(meta["image_count"]),
                "review_text": text_from_ann.get(rid),
                "text_word_count": text.get("text_word_count"),
                "sentiment_negative": text.get("sentiment_negative"),
                "sentiment_neutral": text.get("sentiment_neutral"),
                "sentiment_positive": text.get("sentiment_positive"),
                "usable_image_count": usable,
                "image_status": image_status,
                "text_image_cosine_mean": mean(ok_scores) if ok_scores else None,
                "text_image_cosine_min": min(ok_scores) if ok_scores else None,
                "text_run_id": text.get("run_id"),
                "image_run_id": image_run_id,
            }
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = args.out_dir / "04_review_features_pilot100.jsonl"
    csv_path = args.out_dir / "04_review_features_pilot100.csv"
    report_path = args.out_dir / "acceptance_report_pilot100.json"

    with jsonl_path.open("w", encoding="utf-8") as fh:
        for row in joined:
            fh.write(json.dumps(row) + "\n")

    fields = list(joined[0].keys()) if joined else []
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in joined:
            writer.writerow({k: ("" if v is None else v) for k, v in row.items()})

    report = {
        "passed_partial": True,
        "complete_contract_01": False,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "joined_rows": len(joined),
            "text_features_available": len(text_ids),
            "image_reviews_available": len(rif_ids),
            "overlap_joined": len(overlap),
            "text_without_images": len(text_ids - rif_ids),
            "images_without_text": len(rif_ids - text_ids),
            "image_status": dict(status_counts),
            "review_text_filled_from_annotations": sum(
                1 for row in joined if row["review_text"]
            ),
        },
        "missing_from_pilot_zip": [
            "parent_asin",
            "rating",
            "helpful_vote",
            "verified_purchase",
            "timestamp_ms",
            "full 01_reviews.jsonl",
        ],
        "sources": {
            "text": str(args.text),
            "images": str(images_path),
            "review_image_features": str(rif_path),
            "annotations": str(ann_path),
        },
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Joined {len(joined)} overlapping reviews")
    print(f"  JSONL: {jsonl_path}")
    print(f"  CSV:   {csv_path}")
    print(f"  Report:{report_path}")
    print("image_status:", dict(status_counts))
    print(
        "NOTE: rating/helpful_vote/parent_asin are null — Pilot zip has no full 01_reviews."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
