"""JSONL load/save helpers."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def load_jsonl(path: Path, model: type[T]) -> tuple[list[T], list[str]]:
    """Load JSONL into pydantic models. Returns (rows, parse_errors)."""
    rows: list[T] = []
    errors: list[str] = []
    if not path.exists():
        errors.append(f"File not found: {path}")
        return rows, errors

    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"{path.name}:{line_no}: invalid JSON ({exc})")
                continue
            try:
                rows.append(model.model_validate(payload))
            except ValidationError as exc:
                errors.append(
                    f"{path.name}:{line_no}: schema error ({exc.errors()[0]['msg']})"
                )
    return rows, errors


def write_jsonl(path: Path, rows: list[BaseModel]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(row.model_dump_json() + "\n")


def write_csv_from_models(path: Path, rows: list[BaseModel], fieldnames: list[str]) -> None:
    """Write CSV with blank cells for null (contract convention)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            data = row.model_dump()
            out = {}
            for key in fieldnames:
                value = data.get(key)
                if value is None:
                    out[key] = ""
                elif isinstance(value, bool):
                    out[key] = str(value)
                else:
                    out[key] = value
            writer.writerow(out)
