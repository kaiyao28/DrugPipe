"""Validate standardised GWAS summary-statistic schemas and values."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from osteo_target_gwas.io.read_gwas import REQUIRED_STANDARD_COLUMNS

VALID_ALLELES = {"A", "C", "G", "T"}
VALID_CHROMOSOMES = {str(chromosome) for chromosome in range(1, 23)} | {"X", "Y", "MT"}


def validate_gwas_schema(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Validate standardised GWAS rows and return a summary dictionary."""

    if not rows:
        msg = "GWAS file contains no data rows"
        raise ValueError(msg)

    missing_columns = [column for column in REQUIRED_STANDARD_COLUMNS if column not in rows[0]]
    if missing_columns:
        msg = f"GWAS data is missing required columns: {', '.join(missing_columns)}"
        raise ValueError(msg)

    for index, row in enumerate(rows, start=2):
        _validate_row(row, index)

    return {
        "valid": True,
        "row_count": len(rows),
        "required_columns": REQUIRED_STANDARD_COLUMNS,
        "optional_columns_present": sorted(
            column for column in ("INFO", "OR", "N_CASE", "N_CONTROL") if column in rows[0]
        ),
        "message": f"Validated {len(rows)} GWAS summary-statistic rows.",
    }


def _validate_row(row: dict[str, Any], row_number: int) -> None:
    _validate_chromosome(row["CHR"], row_number)
    _validate_positive_int(row["BP"], "BP", row_number)
    _validate_positive_number(row["N"], "N", row_number)
    _validate_numeric(row["BETA"], "BETA", row_number)
    _validate_positive_number(row["SE"], "SE", row_number)
    _validate_probability(row["P"], "P", row_number)
    _validate_probability(row["EAF"], "EAF", row_number)
    _validate_allele(row["A1"], "A1", row_number)
    _validate_allele(row["A2"], "A2", row_number)


def _validate_probability(value: Any, column: str, row_number: int) -> None:
    number = _as_float(value, column, row_number)
    if not 0 <= number <= 1:
        msg = f"Invalid {column} at row {row_number}: expected value between 0 and 1, got {value!r}"
        raise ValueError(msg)


def _validate_positive_number(value: Any, column: str, row_number: int) -> None:
    number = _as_float(value, column, row_number)
    if number <= 0:
        msg = f"Invalid {column} at row {row_number}: expected positive value, got {value!r}"
        raise ValueError(msg)


def _validate_numeric(value: Any, column: str, row_number: int) -> None:
    _as_float(value, column, row_number)


def _validate_positive_int(value: Any, column: str, row_number: int) -> None:
    try:
        number = int(value)
    except (TypeError, ValueError) as error:
        msg = f"Invalid {column} at row {row_number}: expected positive integer, got {value!r}"
        raise ValueError(msg) from error

    if number <= 0:
        msg = f"Invalid {column} at row {row_number}: expected positive integer, got {value!r}"
        raise ValueError(msg)


def _validate_allele(value: Any, column: str, row_number: int) -> None:
    allele = str(value).upper()
    if allele not in VALID_ALLELES:
        msg = f"Invalid {column} at row {row_number}: expected one of A/C/G/T, got {value!r}"
        raise ValueError(msg)


def _validate_chromosome(value: Any, row_number: int) -> None:
    chromosome = str(value).upper().removeprefix("CHR")
    if chromosome not in VALID_CHROMOSOMES:
        msg = (
            f"Invalid CHR at row {row_number}: expected 1-22, X, Y, or MT, "
            f"got {value!r}"
        )
        raise ValueError(msg)


def _as_float(value: Any, column: str, row_number: int) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        msg = f"Invalid {column} at row {row_number}: expected numeric value, got {value!r}"
        raise ValueError(msg) from error
