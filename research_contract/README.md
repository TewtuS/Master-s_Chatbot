# Team output contract — v1

Person 1 → `01_reviews`  
Person 2 → `02_text_features`  
Person 3 → `03_image_features`  
Person 4 → join into `04_review_features`

JSONL is authoritative. Failure scores stay null (never coerce to 0). Aggregate image rows before joining. Left-join on `review_id` and preserve every review from `01`.

See `backend/README.md` for the Person-4 join tool.
