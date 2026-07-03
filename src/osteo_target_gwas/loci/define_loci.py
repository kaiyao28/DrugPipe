"""Define significant GWAS loci from harmonised summary statistics."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from osteo_target_gwas.config import load_default_config
from osteo_target_gwas.io.read_gwas import read_gwas
from osteo_target_gwas.io.validate_schema import validate_gwas_schema
from osteo_target_gwas.loci.annotate_loci import LOCUS_OUTPUT_COLUMNS, annotate_locus


def define_significant_loci(
    gwas_path: str | Path,
    outdir: str | Path,
    config_path: str | Path = "config/default.yaml",
    p_threshold: float | None = None,
    window_kb: int | None = None,
) -> dict[str, Any]:
    """Define merged genome-wide significant loci and write loci.tsv."""

    config = load_default_config(config_path)
    mappings = config.get("column_mappings", {}).get("gwas_summary_statistics", {})
    locus_settings = config.get("locus_settings", {})
    p_threshold_value = float(
        locus_settings.get("p_threshold", 5e-8) if p_threshold is None else p_threshold
    )
    window_kb_value = int(locus_settings.get("window_kb", 500) if window_kb is None else window_kb)

    rows = read_gwas(gwas_path, mappings)
    validate_gwas_schema(rows)

    significant_rows = sorted(
        [row for row in rows if float(row["P"]) < p_threshold_value],
        key=lambda row: float(row["P"]),
    )

    candidate_loci = [
        {
            "CHR": _normalise_chromosome(row["CHR"]),
            "START": max(1, int(row["BP"]) - window_kb_value * 1000),
            "END": int(row["BP"]) + window_kb_value * 1000,
        }
        for row in significant_rows
    ]
    merged_loci = _merge_overlapping_loci(candidate_loci)
    annotated_loci = [
        annotate_locus(locus, rows, significant_rows)
        for locus in merged_loci
    ]

    output_dir = Path(outdir) / "loci"
    output_dir.mkdir(parents=True, exist_ok=True)
    loci_path = output_dir / "loci.tsv"
    _write_loci(loci_path, annotated_loci)

    return {
        "loci": annotated_loci,
        "loci_path": str(loci_path),
        "n_loci": len(annotated_loci),
        "n_significant_variants": len(significant_rows),
    }


def _merge_overlapping_loci(candidate_loci: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not candidate_loci:
        return []

    ordered = sorted(
        candidate_loci,
        key=lambda locus: (_chromosome_sort_key(locus["CHR"]), int(locus["START"]), int(locus["END"])),
    )
    merged: list[dict[str, Any]] = []

    for locus in ordered:
        if not merged or locus["CHR"] != merged[-1]["CHR"] or locus["START"] > merged[-1]["END"]:
            merged.append(dict(locus))
            continue
        merged[-1]["END"] = max(merged[-1]["END"], locus["END"])

    return merged


def _write_loci(path: Path, loci: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOCUS_OUTPUT_COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerows(loci)


def _normalise_chromosome(chromosome: str) -> str:
    return str(chromosome).upper().removeprefix("CHR")


def _chromosome_sort_key(chromosome: str) -> tuple[int, str]:
    chromosome = _normalise_chromosome(chromosome)
    special = {"X": 23, "Y": 24, "MT": 25}
    if chromosome.isdigit():
        return (int(chromosome), chromosome)
    return (special.get(chromosome, 99), chromosome)
