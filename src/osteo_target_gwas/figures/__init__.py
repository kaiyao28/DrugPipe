"""Conventional plotting recipe entry points for DrugPipe."""

from osteo_target_gwas.figures.effect_estimates import plot_forest
from osteo_target_gwas.figures.enrichment import plot_enrichment_dotplot
from osteo_target_gwas.figures.expression import (
    plot_expression_by_group,
    plot_expression_heatmap,
    plot_ma,
    plot_pca,
    plot_volcano,
)
from osteo_target_gwas.figures.genetics import plot_locus, plot_manhattan, plot_qq
from osteo_target_gwas.figures.targets import plot_evidence_heatmap, plot_target_scores

__all__ = [
    "plot_evidence_heatmap",
    "plot_enrichment_dotplot",
    "plot_expression_by_group",
    "plot_expression_heatmap",
    "plot_forest",
    "plot_locus",
    "plot_ma",
    "plot_manhattan",
    "plot_pca",
    "plot_qq",
    "plot_target_scores",
    "plot_volcano",
]
