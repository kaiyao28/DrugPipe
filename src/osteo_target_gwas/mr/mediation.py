"""Parse precomputed mediation Mendelian randomisation evidence."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

MEDIATION_MR_COLUMNS = [
    "gene_name",
    "mediator",
    "mediator_category",
    "indirect_effect",
    "se",
    "p",
    "proportion_mediated",
]

MEDIATION_MR_OUTPUT_COLUMNS = [
    *MEDIATION_MR_COLUMNS,
    "mediation_score",
]

GENE_MEDIATION_SUMMARY_COLUMNS = [
    "gene_name",
    "best_mediator",
    "best_mediator_category",
    "best_mediation_p",
    "best_proportion_mediated",
    "mediation_score",
]


def read_mediation_mr_results(path: str | Path) -> list[dict[str, str]]:
    """Read, validate, and score precomputed mediation MR results."""

    mediation_path = Path(path)
    with mediation_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)

    if reader.fieldnames is None:
        msg = f"Mediation MR result file {mediation_path} is empty or has no header row"
        raise ValueError(msg)

    missing = [column for column in MEDIATION_MR_COLUMNS if column not in reader.fieldnames]
    if missing:
        msg = (
            f"Mediation MR result file {mediation_path} is missing required columns: "
            f"{', '.join(missing)}"
        )
        raise ValueError(msg)

    scored_rows = []
    for index, row in enumerate(rows, start=2):
        p_value, proportion_mediated = _validate_mediation_row(row, index)
        scored_rows.append(
            {
                **{column: row[column] for column in MEDIATION_MR_COLUMNS},
                "mediation_score": _format_float(_mediation_score(p_value, proportion_mediated)),
            }
        )

    return scored_rows


def summarise_mediation_by_gene(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Summarise each gene by its strongest mediation score."""

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["gene_name"]].append(row)

    summaries = []
    for gene_name, gene_rows in sorted(grouped.items()):
        best = max(
            gene_rows,
            key=lambda row: (float(row["mediation_score"]), -float(row["p"])),
        )
        summaries.append(
            {
                "gene_name": gene_name,
                "best_mediator": best["mediator"],
                "best_mediator_category": best["mediator_category"],
                "best_mediation_p": best["p"],
                "best_proportion_mediated": best["proportion_mediated"],
                "mediation_score": best["mediation_score"],
            }
        )

    return summaries


def run_mediation_mr_parser(
    mediation_path: str | Path,
    outdir: str | Path,
) -> dict[str, Any]:
    """Validate precomputed mediation MR results and write summaries."""

    rows = read_mediation_mr_results(mediation_path)
    summary = summarise_mediation_by_gene(rows)

    output_dir = Path(outdir) / "mr"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_results = output_dir / "mediation_mr_results.tsv"
    output_summary = output_dir / "gene_mediation_summary.tsv"

    _write_tsv(output_results, rows, MEDIATION_MR_OUTPUT_COLUMNS)
    _write_tsv(output_summary, summary, GENE_MEDIATION_SUMMARY_COLUMNS)

    return {
        "mediation_mr_results_path": str(output_results),
        "gene_mediation_summary_path": str(output_summary),
        "n_mediation_records": len(rows),
        "n_genes": len(summary),
    }


def _validate_mediation_row(row: dict[str, str], row_number: int) -> tuple[float, float]:
    _parse_float(row["indirect_effect"], "indirect_effect", row_number)
    se = _parse_float(row["se"], "se", row_number)
    p_value = _parse_float(row["p"], "p", row_number)
    proportion_mediated = _parse_float(
        row["proportion_mediated"],
        "proportion_mediated",
        row_number,
    )

    if not row["mediator"].strip():
        msg = f"Invalid mediator at row {row_number}: expected non-empty value"
        raise ValueError(msg)
    if se <= 0:
        msg = f"Invalid se at row {row_number}: expected value > 0, got {row['se']!r}"
        raise ValueError(msg)
    if not 0 <= p_value <= 1:
        msg = f"Invalid p at row {row_number}: expected value between 0 and 1, got {row['p']!r}"
        raise ValueError(msg)
    if not 0 <= proportion_mediated <= 1:
        msg = (
            f"Invalid proportion_mediated at row {row_number}: expected value between 0 and 1, "
            f"got {row['proportion_mediated']!r}"
        )
        raise ValueError(msg)

    return p_value, proportion_mediated


def _mediation_score(p_value: float, proportion_mediated: float) -> float:
    if p_value <= 0:
        return proportion_mediated
    return min(1.0, -math.log10(p_value) / 10) * proportion_mediated


def _parse_float(value: str, column: str, row_number: int) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        msg = f"Invalid {column} at row {row_number}: expected numeric value, got {value!r}"
        raise ValueError(msg) from error


def _write_tsv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _format_float(value: float) -> str:
    return f"{value:.12g}"
