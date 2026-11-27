"""Thin FastAPI surface for teammate handoffs, validation, and Person-4 join."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from app.join import run_join
from app.paths import (
    HANDOFF_FILES,
    OUTPUT_CSV,
    OUTPUT_JSONL,
    OUTPUT_REPORT,
    RESEARCH_CONTRACT,
    SYNTHETIC_FILES,
    ensure_dirs,
)
from app.report import format_validation_summary
from app.validate import validate_handoffs

PersonKey = Literal["reviews", "text", "images"]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_dirs()
    yield


app = FastAPI(
    title="MIS Person-4 Join Backend",
    description=(
        "Validate teammate handoffs (01/02/03) and join them into 04_review_features. "
        "See research_contract/README.md for field meanings."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "role": "person_4_join"}


@app.get("/contract")
def contract() -> dict:
    readme = RESEARCH_CONTRACT / "README.md"
    return {
        "ownership": {
            "person_1": "01_reviews — one row per review, stable review_id, split, image_count",
            "person_2": "02_text_features — one row per review, sentiment probs, run_id",
            "person_3": "03_image_features — one row per customer image, cosine, run_id",
            "person_4": "04_review_features — left join + image aggregation (this service)",
        },
        "handoff_paths": {k: str(v) for k, v in HANDOFF_FILES.items()},
        "research_contract_dir": str(RESEARCH_CONTRACT),
        "readme_exists": readme.exists(),
        "drive_mapping": {
            "01_reviews": "data/inputs_v2/reviews_image_filtered_v2.jsonl (or reviews_clean subset)",
            "02_text_features": "text_features_image_v2_test.jsonl (or full text features)",
            "03_image_features": (
                "data/image_pipeline/.../integration_preview/image_features_available_v2.jsonl"
            ),
        },
    }


@app.post("/handoffs/{person}")
async def upload_handoff(person: PersonKey, file: UploadFile = File(...)) -> dict:
    ensure_dirs()
    dest = HANDOFF_FILES[person]
    content = await file.read()
    if not content.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    dest.write_bytes(content)
    return {
        "ok": True,
        "person": person,
        "saved_as": str(dest),
        "bytes": len(content),
        "filename": file.filename,
    }


@app.post("/validate")
def validate_current() -> JSONResponse:
    ensure_dirs()
    missing = [k for k, p in HANDOFF_FILES.items() if not p.exists()]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing handoff files for: {missing}. POST /handoffs/{{person}} first.",
        )
    report, _, _, _ = validate_handoffs(
        HANDOFF_FILES["reviews"],
        HANDOFF_FILES["text"],
        HANDOFF_FILES["images"],
    )
    body = report.model_dump()
    body["summary"] = format_validation_summary(report)
    return JSONResponse(content=body, status_code=200 if report.ok else 422)


@app.post("/join")
def join_current() -> JSONResponse:
    ensure_dirs()
    missing = [k for k, p in HANDOFF_FILES.items() if not p.exists()]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing handoff files for: {missing}. POST /handoffs/{{person}} first.",
        )
    result, _ = run_join(
        HANDOFF_FILES["reviews"],
        HANDOFF_FILES["text"],
        HANDOFF_FILES["images"],
    )
    return JSONResponse(
        content=result.model_dump(),
        status_code=200 if result.ok else 422,
    )


@app.get("/outputs/latest")
def outputs_latest() -> dict:
    ensure_dirs()
    report = None
    if OUTPUT_REPORT.exists():
        report = json.loads(OUTPUT_REPORT.read_text(encoding="utf-8"))
    return {
        "jsonl": str(OUTPUT_JSONL) if OUTPUT_JSONL.exists() else None,
        "csv": str(OUTPUT_CSV) if OUTPUT_CSV.exists() else None,
        "report_path": str(OUTPUT_REPORT) if OUTPUT_REPORT.exists() else None,
        "report": report,
        "downloads": {
            "jsonl": "/outputs/download/jsonl",
            "csv": "/outputs/download/csv",
            "report": "/outputs/download/report",
        },
    }


@app.get("/outputs/download/{kind}")
def download_output(kind: Literal["jsonl", "csv", "report"]) -> FileResponse:
    mapping = {
        "jsonl": (OUTPUT_JSONL, "04_review_features.jsonl", "application/x-ndjson"),
        "csv": (OUTPUT_CSV, "04_review_features.csv", "text/csv"),
        "report": (OUTPUT_REPORT, "acceptance_report.json", "application/json"),
    }
    path, filename, media = mapping[kind]
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No {kind} output yet. POST /join first.")
    return FileResponse(path, filename=filename, media_type=media)


@app.post("/demo/synthetic")
def demo_synthetic() -> JSONResponse:
    """Run the golden join on bundled fixtures without overwriting teammate inputs."""
    ensure_dirs()
    result, joined = run_join(
        SYNTHETIC_FILES["reviews"],
        SYNTHETIC_FILES["text"],
        SYNTHETIC_FILES["images"],
    )
    payload = result.model_dump()
    payload["demo"] = {
        "loaded_from": str(RESEARCH_CONTRACT),
        "joined_preview": [row.model_dump() for row in joined[:3]],
    }
    return JSONResponse(content=payload, status_code=200 if result.ok else 422)
