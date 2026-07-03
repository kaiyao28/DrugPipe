"""Bone-cell and tissue-context scoring for mapped genes."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

CELL_TYPES = [
    "osteoblast",
    "osteoclast",
    "osteocyte",
    "mesenchymal_stromal_cell",
    "immune_cell",
]

BONE_CELL_CONTEXT_COLUMNS = [
    "gene_name",
    "osteoblast_score",
    "osteoclast_score",
    "osteocyte_score",
    "mesenchymal_stromal_cell_score",
    "immune_cell_score",
    "top_cell_context",
    "bone_cell_context_score",
]


def score_bone_cell_context(
    gene_map_path: str | Path,
    markers_path: str | Path,
    outdir: str | Path,
) -> dict[str, Any]:
    """Score gene relevance across bone-cell marker contexts."""

    gene_map_rows = _read_tsv(Path(gene_map_path), "locus-gene map")
    marker_rows = _read_tsv(Path(markers_path), "bone-cell marker")
    marker_scores = _aggregate_marker_scores(marker_rows)

    gene_names = sorted({row["gene_name"] for row in gene_map_rows})
    rows = [_score_gene(gene_name, marker_scores) for gene_name in gene_names]

    output_dir = Path(outdir) / "cell_context"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "bone_cell_relevance.tsv"
    _write_tsv(output_path, rows, BONE_CELL_CONTEXT_COLUMNS)

    return {
        "bone_cell_relevance_path": str(output_path),
        "n_genes": len(rows),
        "rows": rows,
    }


def _aggregate_marker_scores(
    marker_rows: list[dict[str, str]],
) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = defaultdict(dict)
    for index, row in enumerate(marker_rows, start=2):
        cell_type = row["cell_type"]
        if cell_type not in CELL_TYPES:
            msg = f"Invalid cell_type at row {index}: expected one of {', '.join(CELL_TYPES)}, got {cell_type!r}"
            raise ValueError(msg)

        marker_strength = _parse_marker_strength(row["marker_strength"], index)
        gene_scores = scores[row["gene_name"]]
        gene_scores[cell_type] = max(marker_strength, gene_scores.get(cell_type, 0.0))

    return scores


def _score_gene(
    gene_name: str,
    marker_scores: dict[str, dict[str, float]],
) -> dict[str, str]:
    gene_scores = marker_scores.get(gene_name, {})
    cell_scores = {cell_type: gene_scores.get(cell_type, 0.0) for cell_type in CELL_TYPES}
    best_cell_type = max(CELL_TYPES, key=lambda cell_type: cell_scores[cell_type])
    best_score = cell_scores[best_cell_type]
    top_cell_context = best_cell_type if best_score > 0 else "unknown"

    return {
        "gene_name": gene_name,
        "osteoblast_score": _format_float(cell_scores["osteoblast"]),
        "osteoclast_score": _format_float(cell_scores["osteoclast"]),
        "osteocyte_score": _format_float(cell_scores["osteocyte"]),
        "mesenchymal_stromal_cell_score": _format_float(cell_scores["mesenchymal_stromal_cell"]),
        "immune_cell_score": _format_float(cell_scores["immune_cell"]),
        "top_cell_context": top_cell_context,
        "bone_cell_context_score": _format_float(best_score),
    }


def _parse_marker_strength(value: str, row_number: int) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError) as error:
        msg = f"Invalid marker_strength at row {row_number}: expected numeric value, got {value!r}"
        raise ValueError(msg) from error

    if not 0 <= score <= 1:
        msg = f"Invalid marker_strength at row {row_number}: expected value between 0 and 1, got {value!r}"
        raise ValueError(msg)

    return score


def _read_tsv(path: Path, label: str) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)

    if reader.fieldnames is None:
        msg = f"{label} file {path} is empty or has no header row"
        raise ValueError(msg)
    return rows


def _write_tsv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _format_float(value: float) -> str:
    return f"{value:.12g}"
