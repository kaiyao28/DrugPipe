"""Druggability and tractability annotation for candidate targets."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

DRUGGABILITY_COLUMNS = [
    "gene_name",
    "target_class",
    "tractability_modality",
    "tractability_score",
    "known_drug",
    "known_drug_name",
    "safety_note",
]

DRUGGABILITY_OUTPUT_COLUMNS = [
    *DRUGGABILITY_COLUMNS,
    "druggability_score",
]

TRUE_VALUES = {"true", "yes", "1", "y"}
FALSE_VALUES = {"false", "no", "0", "n"}


def read_druggability(path: str | Path) -> list[dict[str, str]]:
    """Read, validate, and score druggability annotations."""

    druggability_path = Path(path)
    with druggability_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)

    if reader.fieldnames is None:
        msg = f"Druggability file {druggability_path} is empty or has no header row"
        raise ValueError(msg)

    missing = [column for column in DRUGGABILITY_COLUMNS if column not in reader.fieldnames]
    if missing:
        msg = f"Druggability file {druggability_path} is missing required columns: {', '.join(missing)}"
        raise ValueError(msg)

    scored_rows = []
    for index, row in enumerate(rows, start=2):
        tractability_score = _validate_tractability_score(row["tractability_score"], index)
        known_drug = _parse_bool(row["known_drug"], index)
        druggability_score = min(1.0, tractability_score + (0.1 if known_drug else 0.0))

        if not row["gene_name"].strip():
            msg = f"Invalid gene_name at row {index}: expected non-empty value"
            raise ValueError(msg)

        scored_rows.append(
            {
                **{column: row[column] for column in DRUGGABILITY_COLUMNS},
                "known_drug": str(known_drug).lower(),
                "druggability_score": _format_float(druggability_score),
            }
        )

    return scored_rows


def run_druggability_annotation(
    druggability_path: str | Path,
    outdir: str | Path,
) -> dict[str, Any]:
    """Validate druggability annotations and write scored target records."""

    rows = read_druggability(druggability_path)

    output_dir = Path(outdir) / "targets"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "druggability.tsv"
    _write_tsv(output_path, rows, DRUGGABILITY_OUTPUT_COLUMNS)

    return {
        "druggability_path": str(output_path),
        "n_targets": len(rows),
    }


def _validate_tractability_score(value: str, row_number: int) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError) as error:
        msg = f"Invalid tractability_score at row {row_number}: expected numeric value, got {value!r}"
        raise ValueError(msg) from error

    if not 0 <= score <= 1:
        msg = (
            f"Invalid tractability_score at row {row_number}: expected value between 0 and 1, "
            f"got {value!r}"
        )
        raise ValueError(msg)

    return score


def _parse_bool(value: str, row_number: int) -> bool:
    normalised = str(value).strip().lower()
    if normalised in TRUE_VALUES:
        return True
    if normalised in FALSE_VALUES:
        return False
    msg = f"Invalid known_drug at row {row_number}: expected boolean-like value, got {value!r}"
    raise ValueError(msg)


def _write_tsv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _format_float(value: float) -> str:
    return f"{value:.12g}"
