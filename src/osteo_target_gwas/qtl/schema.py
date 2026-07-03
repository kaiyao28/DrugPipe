"""Schemas and controlled vocabularies for QTL colocalisation evidence."""

from __future__ import annotations

COLOC_COLUMNS = [
    "locus_id",
    "gene_name",
    "qtl_type",
    "tissue_or_cell",
    "pp_h4",
    "pp_h3",
    "effect_direction",
]

GENE_COLOC_SUMMARY_COLUMNS = [
    "gene_name",
    "max_pp_h4",
    "best_qtl_type",
    "best_tissue_or_cell",
    "best_effect_direction",
    "qtl_colocalisation_score",
]

VALID_QTL_TYPES = {"eQTL", "sQTL", "pQTL", "caQTL", "other"}

VALID_EFFECT_DIRECTIONS = {
    "increased_expression_increases_risk",
    "increased_expression_decreases_risk",
    "increased_expression_increases_BMD",
    "increased_expression_decreases_BMD",
    "unknown",
}
