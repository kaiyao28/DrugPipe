"""Conventional genetics plotting recipe placeholders."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def plot_manhattan(gwas_path: str | Path, out: str | Path, **kwargs: Any) -> Path:
    """Create a Manhattan plot from SNP, CHR, BP and P columns."""
    raise NotImplementedError("Manhattan plotting is documented but not implemented in the MVP.")


def plot_qq(gwas_path: str | Path, out: str | Path, **kwargs: Any) -> Path:
    """Create a QQ plot from GWAS p-values."""
    raise NotImplementedError("QQ plotting is documented but not implemented in the MVP.")


def plot_locus(gwas_path: str | Path, locus_id: str, out: str | Path, **kwargs: Any) -> Path:
    """Create a locus-level association plot when locus data are available."""
    raise NotImplementedError("Locus plotting is documented but not implemented in the MVP.")
