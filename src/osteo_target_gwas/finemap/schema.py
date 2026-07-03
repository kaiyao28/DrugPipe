"""Schemas for precomputed fine-mapping inputs and summaries."""

from __future__ import annotations

CREDIBLE_SET_COLUMNS = ["locus_id", "SNP", "CHR", "BP", "PIP", "credible_set", "method"]

LOCUS_FINEMAP_SUMMARY_COLUMNS = [
    "locus_id",
    "CHR",
    "N_VARIANTS",
    "N_CREDIBLE_SETS",
    "TOP_SNP",
    "TOP_PIP",
    "locus_finemap_score",
    "method",
]
