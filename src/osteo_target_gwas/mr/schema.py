"""Schemas for Mendelian randomisation evidence files."""

from __future__ import annotations

MR_RESULT_COLUMNS = [
    "gene_name",
    "exposure_type",
    "exposure_id",
    "outcome",
    "beta",
    "se",
    "p",
    "f_statistic",
    "method",
    "direction",
]

TARGET_MR_OUTPUT_COLUMNS = [
    *MR_RESULT_COLUMNS,
    "strong_instrument",
    "mr_evidence_score",
]

GENE_MR_SUMMARY_COLUMNS = [
    "gene_name",
    "best_exposure_type",
    "best_outcome",
    "best_beta",
    "best_p",
    "best_f_statistic",
    "best_method",
    "mr_direction",
    "mr_target_validation_score",
]
