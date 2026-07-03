"""Read and standardise GWAS summary-statistic files."""

from __future__ import annotations

import csv
import gzip
from pathlib import Path
from typing import Any


REQUIRED_STANDARD_COLUMNS = ["SNP", "CHR", "BP", "A1", "A2", "BETA", "SE", "P", "EAF", "N"]
OPTIONAL_STANDARD_COLUMNS = ["INFO", "OR", "N_CASE", "N_CONTROL"]

SEMANTIC_TO_STANDARD = {
    "variant_id": "SNP",
    "chromosome": "CHR",
    "position": "BP",
    "effect_allele": "A1",
    "other_allele": "A2",
    "effect_size": "BETA",
    "standard_error": "SE",
    "p_value": "P",
    "effect_allele_frequency": "EAF",
    "sample_size": "N",
    "imputation_info": "INFO",
    "odds_ratio": "OR",
    "n_case": "N_CASE",
    "n_control": "N_CONTROL",
}

ALIASES = {
    "SNP": ["SNP", "rsid", "rs_id", "variant", "variant_id"],
    "CHR": ["CHR", "chromosome", "chrom", "chr"],
    "BP": ["BP", "position", "pos", "base_pair_location"],
    "A1": ["A1", "effect_allele", "ea", "alt"],
    "A2": ["A2", "other_allele", "non_effect_allele", "nea", "ref"],
    "BETA": ["BETA", "beta", "effect", "effect_size"],
    "SE": ["SE", "se", "standard_error"],
    "P": ["P", "p", "p_value", "pval", "p_value_gc"],
    "EAF": ["EAF", "eaf", "effect_allele_frequency"],
    "N": ["N", "n", "sample_size"],
    "INFO": ["INFO", "info", "imputation_info"],
    "OR": ["OR", "or", "odds_ratio"],
    "N_CASE": ["N_CASE", "n_case", "cases"],
    "N_CONTROL": ["N_CONTROL", "n_control", "controls"],
}


def read_gwas(path: str | Path, column_mappings: dict[str, Any] | None = None) -> list[dict[str, str]]:
    """Read a GWAS file and standardise core summary-statistic columns."""

    gwas_path = Path(path)
    dialect = _dialect_for_path(gwas_path)

    with _open_text(gwas_path) as handle:
        reader = csv.DictReader(handle, delimiter=dialect)
        rows = list(reader)

    if reader.fieldnames is None:
        msg = f"GWAS file {gwas_path} is empty or has no header row"
        raise ValueError(msg)

    source_columns = _resolve_source_columns(reader.fieldnames, column_mappings)
    missing = [column for column in REQUIRED_STANDARD_COLUMNS if column not in source_columns]
    if missing:
        msg = (
            f"GWAS file {gwas_path} is missing required columns after applying mappings: "
            f"{', '.join(missing)}"
        )
        raise ValueError(msg)

    standardised_rows = []
    for row in rows:
        standardised_row = {
            standard_name: row[source_name]
            for standard_name, source_name in source_columns.items()
            if source_name in row
        }
        standardised_rows.append(standardised_row)

    return standardised_rows


def _open_text(path: Path):
    if path.suffix.lower() == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return path.open("r", encoding="utf-8", newline="")


def _dialect_for_path(path: Path) -> str:
    suffixes = [suffix.lower() for suffix in path.suffixes]
    if suffixes[-2:] == [".tsv", ".gz"] or suffixes[-1:] == [".tsv"]:
        return "\t"
    if suffixes[-2:] == [".csv", ".gz"] or suffixes[-1:] == [".csv"]:
        return ","
    msg = f"Unsupported GWAS file extension for {path}; expected TSV, CSV, TSV.GZ, or CSV.GZ"
    raise ValueError(msg)


def _resolve_source_columns(
    fieldnames: list[str],
    column_mappings: dict[str, Any] | None,
) -> dict[str, str]:
    available = {field.lower(): field for field in fieldnames}
    source_columns: dict[str, str] = {}

    for standard_name in REQUIRED_STANDARD_COLUMNS + OPTIONAL_STANDARD_COLUMNS:
        configured = _configured_source_column(standard_name, column_mappings)
        candidates = [configured] if configured else []
        candidates.extend(ALIASES[standard_name])

        for candidate in candidates:
            if candidate and candidate.lower() in available:
                source_columns[standard_name] = available[candidate.lower()]
                break

    return source_columns


def _configured_source_column(
    standard_name: str,
    column_mappings: dict[str, Any] | None,
) -> str | None:
    if not column_mappings:
        return None

    for semantic_name, mapped_standard_name in SEMANTIC_TO_STANDARD.items():
        if mapped_standard_name == standard_name:
            configured = column_mappings.get(semantic_name)
            if isinstance(configured, str):
                return configured

    configured = column_mappings.get(standard_name)
    if isinstance(configured, str):
        return configured
    return None
