"""Annotate merged GWAS loci with lead variants and variant counts."""

from __future__ import annotations

from typing import Any


LOCUS_OUTPUT_COLUMNS = [
    "locus_id",
    "CHR",
    "START",
    "END",
    "LEAD_SNP",
    "LEAD_BP",
    "LEAD_P",
    "LEAD_BETA",
    "LEAD_SE",
    "N_VARIANTS",
    "N_SIGNIFICANT_VARIANTS",
]


def annotate_locus(
    locus: dict[str, Any],
    rows: list[dict[str, str]],
    significant_rows: list[dict[str, str]],
) -> dict[str, str]:
    """Return a write-ready locus record with lead SNP and variant counts."""

    locus_rows = [
        row
        for row in rows
        if _same_chromosome(row["CHR"], locus["CHR"])
        and locus["START"] <= int(row["BP"]) <= locus["END"]
    ]
    locus_significant_rows = [
        row
        for row in significant_rows
        if _same_chromosome(row["CHR"], locus["CHR"])
        and locus["START"] <= int(row["BP"]) <= locus["END"]
    ]

    lead = min(locus_significant_rows, key=lambda row: float(row["P"]))
    locus_id = f"chr{locus['CHR']}:{locus['START']}-{locus['END']}"

    return {
        "locus_id": locus_id,
        "CHR": str(locus["CHR"]),
        "START": str(locus["START"]),
        "END": str(locus["END"]),
        "LEAD_SNP": lead["SNP"],
        "LEAD_BP": lead["BP"],
        "LEAD_P": lead["P"],
        "LEAD_BETA": lead["BETA"],
        "LEAD_SE": lead["SE"],
        "N_VARIANTS": str(len(locus_rows)),
        "N_SIGNIFICANT_VARIANTS": str(len(locus_significant_rows)),
    }


def _same_chromosome(left: str, right: str) -> bool:
    return _normalise_chromosome(left) == _normalise_chromosome(right)


def _normalise_chromosome(chromosome: str) -> str:
    return str(chromosome).upper().removeprefix("CHR")
