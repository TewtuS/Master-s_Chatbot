"""Filesystem conventions for handoffs, outputs, and research_contract fixtures."""

from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent
RESEARCH_CONTRACT = PROJECT_ROOT / "research_contract"

INPUTS_DIR = BACKEND_ROOT / "inputs"
OUTPUTS_DIR = BACKEND_ROOT / "outputs"

HANDOFF_FILES = {
    "reviews": INPUTS_DIR / "01_reviews.jsonl",
    "text": INPUTS_DIR / "02_text_features.jsonl",
    "images": INPUTS_DIR / "03_image_features.jsonl",
}

SYNTHETIC_FILES = {
    "reviews": RESEARCH_CONTRACT / "01_reviews.synthetic.jsonl",
    "text": RESEARCH_CONTRACT / "02_text_features.synthetic.jsonl",
    "images": RESEARCH_CONTRACT / "03_image_features.synthetic.jsonl",
    "joined": RESEARCH_CONTRACT / "04_review_features.synthetic.jsonl",
    "joined_csv": RESEARCH_CONTRACT / "04_review_features.synthetic.csv",
    "manifest": RESEARCH_CONTRACT / "run_manifest.synthetic.json",
}

OUTPUT_JSONL = OUTPUTS_DIR / "04_review_features.jsonl"
OUTPUT_CSV = OUTPUTS_DIR / "04_review_features.csv"
OUTPUT_REPORT = OUTPUTS_DIR / "acceptance_report.json"


def ensure_dirs() -> None:
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
