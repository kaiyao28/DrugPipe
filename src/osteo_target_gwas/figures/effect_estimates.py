"""Conventional effect-estimate plotting recipe placeholders."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def plot_forest(effects_path: str | Path, out: str | Path, **kwargs: Any) -> Path:
    """Create a forest plot from beta, standard error and p-value columns."""
    raise NotImplementedError("Forest plotting is documented but not implemented in the MVP.")
