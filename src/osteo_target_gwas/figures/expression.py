"""Conventional expression plotting recipe placeholders."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def plot_pca(scores_path: str | Path, out: str | Path, **kwargs: Any) -> Path:
    """Create a PCA/grouping plot from PC scores and metadata."""
    raise NotImplementedError("PCA plotting is documented but not implemented in the MVP.")


def plot_expression_by_group(expression_path: str | Path, metadata_path: str | Path, gene: str, out: str | Path, **kwargs: Any) -> Path:
    """Create an expression-by-group plot for one gene."""
    raise NotImplementedError("Expression-by-group plotting is documented but not implemented in the MVP.")


def plot_expression_heatmap(expression_path: str | Path, genes_path: str | Path, out: str | Path, **kwargs: Any) -> Path:
    """Create an expression heatmap for selected genes."""
    raise NotImplementedError("Expression heatmap plotting is documented but not implemented in the MVP.")


def plot_volcano(de_results_path: str | Path, out: str | Path, **kwargs: Any) -> Path:
    """Create a volcano plot from differential-expression results."""
    raise NotImplementedError("Volcano plotting is documented but not implemented in the MVP.")


def plot_ma(de_results_path: str | Path, out: str | Path, **kwargs: Any) -> Path:
    """Create an MA plot from differential-expression results."""
    raise NotImplementedError("MA plotting is documented but not implemented in the MVP.")
