"""Tests for the DrugPipe analysis-map SVG layout generator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = Path("scripts/figures/build_drugpipe_analysis_map.py")


def load_builder():
    """Load the analysis-map builder module from its script path."""
    spec = importlib.util.spec_from_file_location("build_drugpipe_analysis_map", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_default_layout_validates() -> None:
    """The committed analysis-map geometry should pass all layout checks."""
    builder = load_builder()
    nodes = builder.build_nodes()
    connectors = builder.build_connectors()
    builder.validate_layout(nodes, connectors)


def test_overlap_validation_fails() -> None:
    """Overlapping cards should be rejected."""
    builder = load_builder()
    nodes = builder.build_nodes()
    original = nodes["finemap"]
    nodes["finemap"] = builder.Node(
        name=original.name,
        x=nodes["gwas"].x + 10,
        y=nodes["gwas"].y + 10,
        width=original.width,
        height=original.height,
        title_lines=original.title_lines,
        subtitle_lines=original.subtitle_lines,
        style=original.style,
    )
    with pytest.raises(ValueError, match="overlap|too close"):
        builder.validate_no_overlap(nodes)


def test_text_capacity_validation_fails() -> None:
    """Oversized labels should be rejected before SVG generation."""
    builder = load_builder()
    nodes = {
        "small": builder.Node(
            name="small",
            x=100,
            y=100,
            width=120,
            height=80,
            title_lines=("This title is far too long for the card",),
            subtitle_lines=(),
            style="blue",
        )
    }
    with pytest.raises(ValueError, match="Title text too wide"):
        builder.validate_text_capacity(nodes)


def test_connector_validation_requires_known_nodes() -> None:
    """Connectors should reference existing nodes and anchors."""
    builder = load_builder()
    nodes = builder.build_nodes()
    connectors = (builder.Connector("missing", "bottom", "gwas", "top"),)
    with pytest.raises(ValueError, match="Unknown connector source"):
        builder.validate_connectors(connectors, nodes)


def test_generated_svg_contains_accessible_title() -> None:
    """Generated SVG should expose the expected accessible title."""
    builder = load_builder()
    nodes = builder.build_nodes()
    connectors = builder.build_connectors()
    svg = builder.build_svg(nodes, connectors)
    assert "<title id=\"title\">DrugPipe analysis map</title>" in svg
    assert "Standard evidence tables" in svg


def test_committed_svg_matches_generator() -> None:
    """The committed workflow SVG should be generated from the layout script."""
    builder = load_builder()
    nodes = builder.build_nodes()
    connectors = builder.build_connectors()
    expected_svg = builder.build_svg(nodes, connectors)
    committed_svg = Path("docs/assets/drugpipe-workflow.svg").read_text(encoding="utf-8")
    assert committed_svg == expected_svg
