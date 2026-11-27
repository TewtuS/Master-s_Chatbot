# MIS Person-4 Join Backend

Joins teammate outputs into `04_review_features`.

## What you already have

| Input | Status in this repo |
|-------|---------------------|
| `02_text_features` | Present: `inputs/02_text_features.jsonl` (100-row V2 test) |
| `01_reviews` | **Still needed** from Drive |
| `03_image_features` | **Still needed** from Drive |

### Drive file mapping (from your notebooks)

- **01**: `MKT4220_Project/data/inputs_v2/reviews_image_filtered_v2.jsonl`
- **02**: `text_features_image_v2_test.jsonl` (already copied here)
- **03**: `MKT4220_Project/data/image_pipeline/openclip_vitb32_quickgelu_openai_v1/v2_model_ready/integration_preview/image_features_available_v2.jsonl`

## Quick start

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Prove the join works on synthetic fixtures
python scripts/join_cli.py --synthetic
pytest -q
```

## Join the 100-row test set

1. On Drive / Colab, subset the big files to the text-feature IDs:

```bash
python scripts/subset_handoffs.py \
  --text inputs/02_text_features.jsonl \
  --reviews-src /path/to/reviews_image_filtered_v2.jsonl \
  --images-src /path/to/image_features_available_v2.jsonl \
  --reviews-out inputs/01_reviews.jsonl \
  --images-out inputs/03_image_features.jsonl
```

2. Join:

```bash
python scripts/join_cli.py
```

Outputs land in `outputs/04_review_features.{jsonl,csv}` plus `acceptance_report.json`.

## Colab notebook

See [`../04_Join_Pipeline.ipynb`](../04_Join_Pipeline.ipynb) — mount Drive, subset, validate, join.
