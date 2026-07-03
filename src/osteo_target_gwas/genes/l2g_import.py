"""Import optional locus-to-gene evidence."""

from __future__ import annotations

import csv
from pathlib import Path

L2G_COLUMNS = ["locus_id", "gene_name", "l2g_score", "l2g_evidence_type"]


def read_l2g_scores(path: str | Path | None) -> dict[tuple[str, str], dict[str, str]]:
    """Read optional L2G scores keyed by locus and gene name."""

    if path is None:
        return {}

    l2g_path = Path(path)
    if not l2g_path.exists():
        return {}

    with l2g_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)

    if reader.fieldnames is None:
        return {}

    missing = [column for column in L2G_COLUMNS if column not in reader.fieldnames]
    if missing:
        msg = f"L2G file {l2g_path} is missing required columns: {', '.join(missing)}"
        raise ValueError(msg)

    scores = {}
    for index, row in enumerate(rows, start=2):
        score = _parse_score(row["l2g_score"], index)
        scores[(row["locus_id"], row["gene_name"])] = {
            "l2g_score": _format_float(score),
            "l2g_evidence_type": row["l2g_evidence_type"],
        }

    return scores


def _parse_score(value: str, row_number: int) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError) as error:
        msg = f"Invalid l2g_score at row {row_number}: expected numeric value, got {value!r}"
        raise ValueError(msg) from error

    if not 0 <= score <= 1:
        msg = f"Invalid l2g_score at row {row_number}: expected value between 0 and 1, got {value!r}"
        raise ValueError(msg)

    return score


def _format_float(value: float) -> str:
    return f"{value:.12g}"
