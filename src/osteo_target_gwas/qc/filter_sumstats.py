"""GWAS summary-statistic QC and harmonisation."""

from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path
from typing import Any

from osteo_target_gwas.config import load_default_config
from osteo_target_gwas.io.read_gwas import OPTIONAL_STANDARD_COLUMNS, REQUIRED_STANDARD_COLUMNS, read_gwas
from osteo_target_gwas.io.validate_schema import validate_gwas_schema
from osteo_target_gwas.qc.qc_report import render_qc_report

MISSINGNESS_COLUMNS = ("BETA", "SE", "P")
AMBIGUOUS_ALLELE_PAIRS = {("A", "T"), ("T", "A"), ("C", "G"), ("G", "C")}
OUTPUT_OPTIONAL_COLUMNS = ["MAF", *OPTIONAL_STANDARD_COLUMNS]


def run_gwas_qc(
    gwas_path: str | Path,
    outdir: str | Path,
    config_path: str | Path = "config/default.yaml",
    min_info: float | None = None,
    min_maf: float | None = None,
    remove_ambiguous: bool | None = None,
) -> dict[str, Any]:
    """Read, validate, filter, harmonise, and write GWAS summary statistics."""

    config = load_default_config(config_path)
    mappings = config.get("column_mappings", {}).get("gwas_summary_statistics", {})
    qc_thresholds = config.get("qc_thresholds", {})
    min_info_value = float(qc_thresholds.get("min_info", 0.8) if min_info is None else min_info)
    min_maf_value = float(qc_thresholds.get("min_maf", 0.01) if min_maf is None else min_maf)
    remove_ambiguous_value = bool(
        qc_thresholds.get("remove_ambiguous", True) if remove_ambiguous is None else remove_ambiguous
    )

    rows = read_gwas(gwas_path, mappings)
    n_input = len(rows)

    rows, n_removed_missing = _remove_missing_effect_rows(rows)
    validate_gwas_schema(rows)

    rows, n_removed_low_info = _remove_low_info(rows, min_info_value)
    rows = [_add_maf(row) for row in rows]
    rows, n_removed_low_maf = _remove_low_maf(rows, min_maf_value)
    rows, n_removed_ambiguous = _remove_ambiguous(rows, remove_ambiguous_value)

    summary = _build_summary(
        rows=rows,
        n_input=n_input,
        n_removed_low_info=n_removed_low_info,
        n_removed_low_maf=n_removed_low_maf,
        n_removed_missing=n_removed_missing,
        n_removed_ambiguous=n_removed_ambiguous,
    )

    output_dir = Path(outdir) / "qc"
    output_dir.mkdir(parents=True, exist_ok=True)
    harmonised_path = output_dir / "harmonised_sumstats.tsv.gz"
    summary_path = output_dir / "qc_summary.json"
    report_path = output_dir / "qc_report.md"

    _write_harmonised_sumstats(harmonised_path, rows)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_qc_report(summary), encoding="utf-8")

    return {
        "summary": summary,
        "harmonised_sumstats_path": str(harmonised_path),
        "qc_summary_path": str(summary_path),
        "qc_report_path": str(report_path),
    }


def _remove_missing_effect_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    kept = [row for row in rows if all(str(row.get(column, "")).strip() for column in MISSINGNESS_COLUMNS)]
    return kept, len(rows) - len(kept)


def _remove_low_info(rows: list[dict[str, str]], min_info: float) -> tuple[list[dict[str, str]], int]:
    if not rows or "INFO" not in rows[0]:
        return rows, 0

    kept = [row for row in rows if float(row["INFO"]) >= min_info]
    return kept, len(rows) - len(kept)


def _add_maf(row: dict[str, str]) -> dict[str, str]:
    harmonised = dict(row)
    eaf = float(harmonised["EAF"])
    harmonised["MAF"] = _format_float(min(eaf, 1 - eaf))
    return harmonised


def _remove_low_maf(rows: list[dict[str, str]], min_maf: float) -> tuple[list[dict[str, str]], int]:
    kept = [row for row in rows if float(row["MAF"]) >= min_maf]
    return kept, len(rows) - len(kept)


def _remove_ambiguous(
    rows: list[dict[str, str]],
    remove_ambiguous: bool,
) -> tuple[list[dict[str, str]], int]:
    if not remove_ambiguous:
        return rows, 0

    kept = [
        row
        for row in rows
        if (row["A1"].upper(), row["A2"].upper()) not in AMBIGUOUS_ALLELE_PAIRS
    ]
    return kept, len(rows) - len(kept)


def _build_summary(
    rows: list[dict[str, str]],
    n_input: int,
    n_removed_low_info: int,
    n_removed_low_maf: int,
    n_removed_missing: int,
    n_removed_ambiguous: int,
) -> dict[str, Any]:
    p_values = [float(row["P"]) for row in rows]
    return {
        "n_input_variants": n_input,
        "n_output_variants": len(rows),
        "n_removed_low_info": n_removed_low_info,
        "n_removed_low_maf": n_removed_low_maf,
        "n_removed_missing": n_removed_missing,
        "n_removed_ambiguous": n_removed_ambiguous,
        "min_p": min(p_values) if p_values else None,
        "n_genome_wide_significant": sum(p_value < 5e-8 for p_value in p_values),
    }


def _write_harmonised_sumstats(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        columns = [*REQUIRED_STANDARD_COLUMNS, "MAF"]
    else:
        columns = [
            *REQUIRED_STANDARD_COLUMNS,
            *(column for column in OUTPUT_OPTIONAL_COLUMNS if column in rows[0]),
        ]

    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _format_float(value: float) -> str:
    return f"{value:.12g}"
