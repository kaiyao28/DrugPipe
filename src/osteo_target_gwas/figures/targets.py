"""Conventional target-evidence plotting recipe placeholders."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def plot_target_scores(targets_path: str | Path, out: str | Path, **kwargs: Any) -> Path:
    """Create a ranked target-score plot."""
    raise NotImplementedError("Target-score plotting is documented but not implemented in the MVP.")


def plot_evidence_heatmap(targets_path: str | Path, out: str | Path, **kwargs: Any) -> Path:
    """Create a heatmap comparing evidence layers across targets."""
    raise NotImplementedError("Evidence heatmap plotting is documented but not implemented in the MVP.")
