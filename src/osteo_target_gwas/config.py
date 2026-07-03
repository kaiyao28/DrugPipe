"""Configuration loading for pipeline execution and data-source registries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

@dataclass(frozen=True)
class PipelineConfig:
    """Minimal pipeline configuration shared by command implementations."""

    work_dir: Path = Path("work")
    results_dir: Path = Path("results")
    log_level: str = "INFO"


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML mapping from disk."""

    yaml_path = Path(path)
    with yaml_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if data is None:
        return {}
    if not isinstance(data, dict):
        msg = f"Expected YAML mapping in {yaml_path}"
        raise TypeError(msg)
    return data


def load_default_config(path: str | Path = "config/default.yaml") -> dict[str, Any]:
    """Load the default pipeline configuration."""

    return load_yaml(path)


def load_data_sources(path: str | Path = "config/data_sources.yaml") -> dict[str, Any]:
    """Load the external data-source registry."""

    return load_yaml(path)


def get_scoring_weights(config: dict[str, Any]) -> dict[str, float]:
    """Return target-scoring weights as floats."""

    weights = config.get("scoring_weights", {})
    if not isinstance(weights, dict):
        msg = "Expected 'scoring_weights' to be a mapping"
        raise TypeError(msg)
    return {str(name): float(value) for name, value in weights.items()}
