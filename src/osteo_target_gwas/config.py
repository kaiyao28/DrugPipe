"""Configuration models for pipeline execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    """Minimal pipeline configuration shared by command implementations."""

    work_dir: Path = Path("work")
    results_dir: Path = Path("results")
    log_level: str = "INFO"
