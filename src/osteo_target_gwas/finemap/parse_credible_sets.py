"""Parse and summarise precomputed fine-mapping credible sets."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from osteo_target_gwas.finemap.schema import (
    CREDIBLE_SET_COLUMNS,
    LOCUS_FINEMAP_SUMMARY_COLUMNS,
)


def read_credible_sets(path: str | Path) -> list[dict[str, str]]:
    """Read and validate precomputed credible-set records."""

    credible_sets_path = Path(path)
    with credible_sets_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)

    if reader.fieldnames is None:
        msg = f"Credible-set file {credible_sets_path} is empty or has no header row"
        raise ValueError(msg)

    missing = [column for column in CREDIBLE_SET_COLUMNS if column not in reader.fieldnames]
    if missing:
        msg = f"Credible-set file {credible_sets_path} is missing required columns: {', '.join(missing)}"
        raise ValueError(msg)

    for index, row in enumerate(rows, start=2):
        _validate_row(row, index)

    return [{column: row[column] for column in CREDIBLE_SET_COLUMNS} for row in rows]


def summarise_finemap_by_locus(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Calculate max-PIP fine-mapping scores per locus."""

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["locus_id"]].append(row)

    summaries = []
    for locus_id, locus_rows in sorted(grouped.items()):
        top = max(locus_rows, key=lambda row: float(row["PIP"]))
        credible_sets = {row["credible_set"] for row in locus_rows}
        methods = sorted({row["method"] for row in locus_rows})
        top_pip = float(top["PIP"])
        summaries.append(
            {
                "locus_id": locus_id,
                "CHR": top["CHR"],
                "N_VARIANTS": str(len(locus_rows)),
                "N_CREDIBLE_SETS": str(len(credible_sets)),
                "TOP_SNP": top["SNP"],
                "TOP_PIP": _format_float(top_pip),
                "locus_finemap_score": _format_float(top_pip),
                "method": ",".join(methods),
            }
        )

    return summaries


def summarise_finemap_by_gene(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Alias for locus-level summaries until variant-to-gene mapping is available."""

    return summarise_finemap_by_locus(rows)


def write_credible_sets(path: str | Path, rows: list[dict[str, str]]) -> None:
    """Write normalised credible-set records."""

    _write_tsv(Path(path), rows, CREDIBLE_SET_COLUMNS)


def write_locus_finemap_summary(path: str | Path, rows: list[dict[str, str]]) -> None:
    """Write locus-level fine-mapping summary records."""

    _write_tsv(Path(path), rows, LOCUS_FINEMAP_SUMMARY_COLUMNS)


def _validate_row(row: dict[str, Any], row_number: int) -> None:
    try:
        pip = float(row["PIP"])
    except (TypeError, ValueError) as error:
        msg = f"Invalid PIP at row {row_number}: expected numeric value, got {row['PIP']!r}"
        raise ValueError(msg) from error

    if not 0 <= pip <= 1:
        msg = f"Invalid PIP at row {row_number}: expected value between 0 and 1, got {row['PIP']!r}"
        raise ValueError(msg)

    try:
        int(row["BP"])
    except (TypeError, ValueError) as error:
        msg = f"Invalid BP at row {row_number}: expected integer value, got {row['BP']!r}"
        raise ValueError(msg) from error


def _write_tsv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _format_float(value: float) -> str:
    return f"{value:.12g}"
