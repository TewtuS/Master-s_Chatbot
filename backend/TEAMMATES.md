# Person 4 needs these files

## Person 1 — `01_reviews.jsonl`
Fields: `review_id`, `parent_asin`, `rating`, `helpful_vote`, `verified_purchase`, `timestamp_ms`, `image_count`, `review_text`, `split`

Source on Drive: `data/inputs_v2/reviews_image_filtered_v2.jsonl`

## Person 2 — `02_text_features.jsonl`
Fields: `review_id`, `status`, `sentiment_*`, `text_word_count`, `error_code`, `run_id`

Already received for the 100-row V2 test set.

## Person 3 — `03_image_features.jsonl`
Fields: `review_id`, `image_id`, `image_index`, `image_source`, `status`, `width_px`, `height_px`, `brightness_mean`, `text_image_cosine`, `error_code`, `run_id`

Source on Drive: `.../integration_preview/image_features_available_v2.jsonl`  
Failures must keep cosine **null** (never 0). No rows for reviews with zero images.
