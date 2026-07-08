"""Shared helpers for future standard plotting recipes."""

from __future__ import annotations

from pathlib import Path


def require_columns(columns: set[str], required: set[str], label: str) -> None:
    """Raise a clear error when a plotting input is missing required columns."""
    missing = sorted(required - columns)
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")


def normalise_output_path(path: str | Path) -> Path:
    """Return an output path and create its parent directory."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path
