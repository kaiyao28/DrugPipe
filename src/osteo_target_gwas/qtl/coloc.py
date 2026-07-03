"""Parse and summarise precomputed QTL colocalisation results."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from osteo_target_gwas.qtl.schema import (
    COLOC_COLUMNS,
    GENE_COLOC_SUMMARY_COLUMNS,
    VALID_EFFECT_DIRECTIONS,
    VALID_QTL_TYPES,
)


def read_coloc_results(path: str | Path) -> list[dict[str, str]]:
    """Read and validate precomputed colocalisation results."""

    coloc_path = Path(path)
    with coloc_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)

    if reader.fieldnames is None:
        msg = f"Coloc file {coloc_path} is empty or has no header row"
        raise ValueError(msg)

    missing = [column for column in COLOC_COLUMNS if column not in reader.fieldnames]
    if missing:
        msg = f"Coloc file {coloc_path} is missing required columns: {', '.join(missing)}"
        raise ValueError(msg)

    for index, row in enumerate(rows, start=2):
        _validate_coloc_row(row, index)

    return [{column: row[column] for column in COLOC_COLUMNS} for row in rows]


def summarise_coloc_by_gene(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Summarise each gene by its strongest PP.H4 colocalisation record."""

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["gene_name"]].append(row)

    summaries = []
    for gene_name, gene_rows in sorted(grouped.items()):
        best = max(gene_rows, key=lambda row: float(row["pp_h4"]))
        max_pp_h4 = float(best["pp_h4"])
        summaries.append(
            {
                "gene_name": gene_name,
                "max_pp_h4": _format_float(max_pp_h4),
                "best_qtl_type": best["qtl_type"],
                "best_tissue_or_cell": best["tissue_or_cell"],
                "best_effect_direction": best["effect_direction"],
                "qtl_colocalisation_score": _format_float(max_pp_h4),
            }
        )

    return summaries


def run_coloc_parser(
    coloc_path: str | Path,
    outdir: str | Path,
) -> dict[str, Any]:
    """Validate precomputed coloc results and write standardised outputs."""

    rows = read_coloc_results(coloc_path)
    summary = summarise_coloc_by_gene(rows)

    output_dir = Path(outdir) / "qtl"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_coloc = output_dir / "coloc_results.tsv"
    output_summary = output_dir / "gene_coloc_summary.tsv"

    _write_tsv(output_coloc, rows, COLOC_COLUMNS)
    _write_tsv(output_summary, summary, GENE_COLOC_SUMMARY_COLUMNS)

    return {
        "coloc_results_path": str(output_coloc),
        "gene_coloc_summary_path": str(output_summary),
        "n_coloc_records": len(rows),
        "n_genes": len(summary),
    }


def _validate_coloc_row(row: dict[str, str], row_number: int) -> None:
    _validate_probability(row["pp_h4"], "pp_h4", row_number)
    _validate_probability(row["pp_h3"], "pp_h3", row_number)

    if row["qtl_type"] not in VALID_QTL_TYPES:
        msg = (
            f"Invalid qtl_type at row {row_number}: expected one of "
            f"{', '.join(sorted(VALID_QTL_TYPES))}, got {row['qtl_type']!r}"
        )
        raise ValueError(msg)

    if row["effect_direction"] not in VALID_EFFECT_DIRECTIONS:
        msg = (
            f"Invalid effect_direction at row {row_number}: expected one of "
            f"{', '.join(sorted(VALID_EFFECT_DIRECTIONS))}, got {row['effect_direction']!r}"
        )
        raise ValueError(msg)


def _validate_probability(value: str, column: str, row_number: int) -> None:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        msg = f"Invalid {column} at row {row_number}: expected numeric value, got {value!r}"
        raise ValueError(msg) from error

    if not 0 <= number <= 1:
        msg = f"Invalid {column} at row {row_number}: expected value between 0 and 1, got {value!r}"
        raise ValueError(msg)


def _write_tsv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _format_float(value: float) -> str:
    return f"{value:.12g}"
