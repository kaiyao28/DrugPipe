"""Conventional enrichment plotting recipe placeholders."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def plot_enrichment_dotplot(enrichment_path: str | Path, out: str | Path, **kwargs: Any) -> Path:
    """Create an enrichment dotplot from pathway p-values and gene counts."""
    raise NotImplementedError("Enrichment dotplotting is documented but not implemented in the MVP.")
