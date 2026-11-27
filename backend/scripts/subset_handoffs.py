#!/usr/bin/env python3
"""Filter large Drive exports down to the review_ids in a text-features file.

Use this when Person 2 already produced a small test set (e.g. 100 rows) and you
need matching 01_reviews + 03_image_features slices from the full V2 files.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            ids.add(json.loads(line)["review_id"])
    return ids


def filter_jsonl(src: Path, dest: Path, ids: set[str], id_field: str = "review_id") -> int:
    kept = 0
    dest.parent.mkdir(parents=True, exist_ok=True)
    with src.open("r", encoding="utf-8") as inn, dest.open("w", encoding="utf-8") as out:
        for line in inn:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get(id_field) in ids:
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                kept += 1
    return kept


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--text",
        type=Path,
        required=True,
        help="02_text_features JSONL whose review_ids define the subset",
    )
    parser.add_argument(
        "--reviews-src",
        type=Path,
        required=True,
        help="Full 01 reviews JSONL (e.g. reviews_image_filtered_v2.jsonl)",
    )
    parser.add_argument(
        "--images-src",
        type=Path,
        required=True,
        help="Full 03 image features JSONL (e.g. image_features_available_v2.jsonl)",
    )
    parser.add_argument("--reviews-out", type=Path, required=True)
    parser.add_argument("--images-out", type=Path, required=True)
    args = parser.parse_args(argv)

    ids = load_ids(args.text)
    print(f"Target review_ids: {len(ids)}")
    n_reviews = filter_jsonl(args.reviews_src, args.reviews_out, ids)
    n_images = filter_jsonl(args.images_src, args.images_out, ids)
    print(f"Wrote {n_reviews} reviews -> {args.reviews_out}")
    print(f"Wrote {n_images} image rows -> {args.images_out}")

    missing_reviews = len(ids) - n_reviews
    if missing_reviews:
        print(f"WARNING: {missing_reviews} text review_ids not found in reviews source", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
