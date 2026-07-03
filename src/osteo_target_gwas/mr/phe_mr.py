"""Parse precomputed Phe-MR safety scan results."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

PHE_MR_COLUMNS = [
    "gene_name",
    "outcome_trait",
    "beta",
    "se",
    "p",
    "category",
    "safety_flag",
]

PHE_MR_OUTPUT_COLUMNS = [
    *PHE_MR_COLUMNS,
    "possible_liability",
    "safety_penalty",
]

GENE_PHE_MR_SUMMARY_COLUMNS = [
    "gene_name",
    "n_phe_outcomes",
    "n_liability_flags",
    "strongest_liability_trait",
    "strongest_liability_p",
    "phe_mr_safety_penalty",
]

VALID_SAFETY_FLAGS = {"none", "monitor", "liability", "protective", "unknown"}
SAFETY_PENALTIES = {
    "none": 0.0,
    "monitor": 0.10,
    "liability": 0.25,
    "protective": 0.0,
    "unknown": 0.0,
}
LIABILITY_FLAGS = {"monitor", "liability"}


def read_phe_mr_results(path: str | Path) -> list[dict[str, str]]:
    """Read, validate, and score precomputed Phe-MR safety scan results."""

    phe_mr_path = Path(path)
    with phe_mr_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)

    if reader.fieldnames is None:
        msg = f"Phe-MR result file {phe_mr_path} is empty or has no header row"
        raise ValueError(msg)

    missing = [column for column in PHE_MR_COLUMNS if column not in reader.fieldnames]
    if missing:
        msg = f"Phe-MR result file {phe_mr_path} is missing required columns: {', '.join(missing)}"
        raise ValueError(msg)

    scored_rows = []
    for index, row in enumerate(rows, start=2):
        p_value = _validate_phe_mr_row(row, index)
        possible_liability = p_value < 0.05 and row["safety_flag"] in LIABILITY_FLAGS
        scored_rows.append(
            {
                **{column: row[column] for column in PHE_MR_COLUMNS},
                "possible_liability": str(possible_liability).lower(),
                "safety_penalty": _format_float(SAFETY_PENALTIES[row["safety_flag"]]),
            }
        )

    return scored_rows


def summarise_phe_mr_by_gene(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Summarise Phe-MR safety signals per gene."""

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["gene_name"]].append(row)

    summaries = []
    for gene_name, gene_rows in sorted(grouped.items()):
        liability_rows = [row for row in gene_rows if row["possible_liability"] == "true"]
        strongest = min(liability_rows, key=lambda row: float(row["p"])) if liability_rows else None
        penalty = max(float(row["safety_penalty"]) for row in liability_rows) if liability_rows else 0.0
        summaries.append(
            {
                "gene_name": gene_name,
                "n_phe_outcomes": str(len(gene_rows)),
                "n_liability_flags": str(len(liability_rows)),
                "strongest_liability_trait": strongest["outcome_trait"] if strongest else "none",
                "strongest_liability_p": strongest["p"] if strongest else "",
                "phe_mr_safety_penalty": _format_float(penalty),
            }
        )

    return summaries


def run_phe_mr_parser(
    phe_mr_path: str | Path,
    outdir: str | Path,
) -> dict[str, Any]:
    """Validate precomputed Phe-MR results and write safety summaries."""

    rows = read_phe_mr_results(phe_mr_path)
    summary = summarise_phe_mr_by_gene(rows)

    output_dir = Path(outdir) / "mr"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_results = output_dir / "phe_mr_results.tsv"
    output_summary = output_dir / "gene_phe_mr_safety_summary.tsv"

    _write_tsv(output_results, rows, PHE_MR_OUTPUT_COLUMNS)
    _write_tsv(output_summary, summary, GENE_PHE_MR_SUMMARY_COLUMNS)

    return {
        "phe_mr_results_path": str(output_results),
        "gene_phe_mr_safety_summary_path": str(output_summary),
        "n_phe_mr_records": len(rows),
        "n_genes": len(summary),
    }


def _validate_phe_mr_row(row: dict[str, str], row_number: int) -> float:
    _parse_float(row["beta"], "beta", row_number)
    se = _parse_float(row["se"], "se", row_number)
    p_value = _parse_float(row["p"], "p", row_number)

    if se <= 0:
        msg = f"Invalid se at row {row_number}: expected value > 0, got {row['se']!r}"
        raise ValueError(msg)
    if not 0 <= p_value <= 1:
        msg = f"Invalid p at row {row_number}: expected value between 0 and 1, got {row['p']!r}"
        raise ValueError(msg)
    if row["safety_flag"] not in VALID_SAFETY_FLAGS:
        msg = (
            f"Invalid safety_flag at row {row_number}: expected one of "
            f"{', '.join(sorted(VALID_SAFETY_FLAGS))}, got {row['safety_flag']!r}"
        )
        raise ValueError(msg)

    return p_value


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
