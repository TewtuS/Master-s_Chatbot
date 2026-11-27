#!/usr/bin/env python3
"""One-command local join for Person 4 (no API required)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.join import run_join
from app.paths import (
    HANDOFF_FILES,
    OUTPUT_CSV,
    OUTPUT_JSONL,
    OUTPUT_REPORT,
    SYNTHETIC_FILES,
)
from app.report import format_validation_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and join 01/02/03 handoffs into 04_review_features."
    )
    parser.add_argument("--reviews", type=Path, default=None)
    parser.add_argument("--text", type=Path, default=None)
    parser.add_argument("--images", type=Path, default=None)
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--out-jsonl", type=Path, default=OUTPUT_JSONL)
    parser.add_argument("--out-csv", type=Path, default=OUTPUT_CSV)
    parser.add_argument("--report", type=Path, default=OUTPUT_REPORT)
    args = parser.parse_args(argv)

    if args.synthetic:
        reviews = SYNTHETIC_FILES["reviews"]
        text = SYNTHETIC_FILES["text"]
        images = SYNTHETIC_FILES["images"]
    else:
        reviews = args.reviews or HANDOFF_FILES["reviews"]
        text = args.text or HANDOFF_FILES["text"]
        images = args.images or HANDOFF_FILES["images"]

    for label, path in (("reviews", reviews), ("text", text), ("images", images)):
        if not path.exists():
            print(f"Missing {label} file: {path}", file=sys.stderr)
            return 2

    result, _ = run_join(
        reviews,
        text,
        images,
        output_jsonl=args.out_jsonl,
        output_csv=args.out_csv,
        report_path=args.report,
    )

    print(format_validation_summary(result.validation))
    if result.ok:
        print(f"Joined {result.row_count} rows")
        print(f"  JSONL: {result.output_jsonl}")
        print(f"  CSV:   {result.output_csv}")
        print(f"  Report:{result.report_path}")
        return 0

    print("Join blocked until validation errors are fixed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
