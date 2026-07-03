"""Parse precomputed druggable genome-wide Mendelian randomisation evidence."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from osteo_target_gwas.mr.schema import (
    GENE_MR_SUMMARY_COLUMNS,
    MR_RESULT_COLUMNS,
    TARGET_MR_OUTPUT_COLUMNS,
)


def read_mr_results(path: str | Path) -> list[dict[str, str]]:
    """Read, validate, and score precomputed MR results."""

    mr_path = Path(path)
    with mr_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)

    if reader.fieldnames is None:
        msg = f"MR result file {mr_path} is empty or has no header row"
        raise ValueError(msg)

    missing = [column for column in MR_RESULT_COLUMNS if column not in reader.fieldnames]
    if missing:
        msg = f"MR result file {mr_path} is missing required columns: {', '.join(missing)}"
        raise ValueError(msg)

    scored_rows = []
    for index, row in enumerate(rows, start=2):
        beta, se, p_value, f_statistic = _validate_mr_row(row, index)
        strong_instrument = f_statistic >= 10
        score = _mr_evidence_score(p_value, strong_instrument)
        scored_rows.append(
            {
                **{column: row[column] for column in MR_RESULT_COLUMNS},
                "strong_instrument": str(strong_instrument).lower(),
                "mr_evidence_score": _format_float(score),
            }
        )

    return scored_rows


def summarise_mr_by_gene(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Choose the strongest MR evidence per gene by lowest p-value."""

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["gene_name"]].append(row)

    summaries = []
    for gene_name, gene_rows in sorted(grouped.items()):
        best = min(gene_rows, key=lambda row: float(row["p"]))
        summaries.append(
            {
                "gene_name": gene_name,
                "best_exposure_type": best["exposure_type"],
                "best_outcome": best["outcome"],
                "best_beta": best["beta"],
                "best_p": best["p"],
                "best_f_statistic": best["f_statistic"],
                "best_method": best["method"],
                "mr_direction": best["direction"],
                "mr_target_validation_score": best["mr_evidence_score"],
            }
        )

    return summaries


def run_target_mr_parser(
    mr_path: str | Path,
    outdir: str | Path,
) -> dict[str, Any]:
    """Validate precomputed MR results and write target-level summaries."""

    rows = read_mr_results(mr_path)
    summary = summarise_mr_by_gene(rows)

    output_dir = Path(outdir) / "mr"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_results = output_dir / "target_mr_results.tsv"
    output_summary = output_dir / "gene_mr_summary.tsv"

    _write_tsv(output_results, rows, TARGET_MR_OUTPUT_COLUMNS)
    _write_tsv(output_summary, summary, GENE_MR_SUMMARY_COLUMNS)

    return {
        "target_mr_results_path": str(output_results),
        "gene_mr_summary_path": str(output_summary),
        "n_mr_records": len(rows),
        "n_genes": len(summary),
    }


def _validate_mr_row(row: dict[str, str], row_number: int) -> tuple[float, float, float, float]:
    beta = _parse_float(row["beta"], "beta", row_number)
    se = _parse_float(row["se"], "se", row_number)
    p_value = _parse_float(row["p"], "p", row_number)
    f_statistic = _parse_float(row["f_statistic"], "f_statistic", row_number)

    if se <= 0:
        msg = f"Invalid se at row {row_number}: expected value > 0, got {row['se']!r}"
        raise ValueError(msg)
    if not 0 <= p_value <= 1:
        msg = f"Invalid p at row {row_number}: expected value between 0 and 1, got {row['p']!r}"
        raise ValueError(msg)
    if f_statistic < 0:
        msg = (
            f"Invalid f_statistic at row {row_number}: expected value >= 0, "
            f"got {row['f_statistic']!r}"
        )
        raise ValueError(msg)
    if not row["method"].strip():
        msg = f"Invalid method at row {row_number}: expected non-empty value"
        raise ValueError(msg)

    return beta, se, p_value, f_statistic


def _mr_evidence_score(p_value: float, strong_instrument: bool) -> float:
    if not strong_instrument:
        return 0.0
    if p_value <= 0:
        return 1.0
    return min(1.0, -math.log10(p_value) / 10)


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
