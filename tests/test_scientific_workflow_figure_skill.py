"""Generic tests for the scientific workflow figure skill tooling."""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest


SKILL_DIR = Path(".agents/skills/scientific-workflow-figure")
SPEC_TO_DOT = SKILL_DIR / "scripts" / "spec_to_dot.py"
RENDER_GRAPHVIZ = SKILL_DIR / "scripts" / "render_graphviz.py"
THEMES = SKILL_DIR / "assets" / "themes.yaml"


def load_module(path: Path, name: str):
    """Load a skill helper module from a path."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def example_spec() -> dict:
    """Return a small generic workflow spec."""
    return {
        "figure": {
            "title": "Data-cleaning workflow",
            "subtitle": "From raw data to QC report",
            "pattern": "linear",
            "direction": "LR",
        },
        "nodes": [
            {"id": "raw", "title": "Raw data", "subtitle": "tables", "theme": "input"},
            {"id": "schema", "title": "Schema validation", "subtitle": "types", "theme": "analysis"},
            {"id": "report", "title": "QC report", "subtitle": "reviewed", "theme": "output"},
        ],
        "edges": [
            {"source": "raw", "target": "schema"},
            {"source": "schema", "target": "report", "label": "reviewed edge"},
        ],
        "groups": [{"id": "qc", "label": "Quality control", "nodes": ["schema"]}],
    }


def test_spec_to_dot_rejects_duplicate_node_ids() -> None:
    """Duplicate node IDs should fail validation."""
    spec_to_dot = load_module(SPEC_TO_DOT, "spec_to_dot_duplicate")
    spec = example_spec()
    spec["nodes"].append({"id": "raw", "title": "Another raw", "theme": "input"})
    with pytest.raises(ValueError, match="Duplicate node IDs"):
        spec_to_dot.validate_spec(spec)


def test_spec_to_dot_rejects_missing_edge_endpoint() -> None:
    """Edges should reference known node IDs."""
    spec_to_dot = load_module(SPEC_TO_DOT, "spec_to_dot_endpoint")
    spec = example_spec()
    spec["edges"].append({"source": "raw", "target": "missing"})
    with pytest.raises(ValueError, match="Unknown edge target"):
        spec_to_dot.validate_spec(spec)


def test_spec_to_dot_rejects_invalid_group_reference() -> None:
    """Groups should reference known node IDs."""
    spec_to_dot = load_module(SPEC_TO_DOT, "spec_to_dot_group")
    spec = example_spec()
    spec["groups"][0]["nodes"].append("missing")
    with pytest.raises(ValueError, match="references unknown node"):
        spec_to_dot.validate_spec(spec)


def test_spec_to_dot_output_is_deterministic_and_uses_rank_direction() -> None:
    """The same spec should produce stable DOT with the requested direction."""
    spec_to_dot = load_module(SPEC_TO_DOT, "spec_to_dot_deterministic")
    themes = spec_to_dot.load_themes(THEMES)
    first = spec_to_dot.build_dot(example_spec(), themes)
    second = spec_to_dot.build_dot(example_spec(), themes)
    assert first == second
    assert 'rankdir="LR"' in first
    assert "raw -> schema" in first


def test_spec_to_dot_applies_semantic_theme_mapping() -> None:
    """Theme names should map to configured fill, border and text colours."""
    spec_to_dot = load_module(SPEC_TO_DOT, "spec_to_dot_theme")
    themes = spec_to_dot.load_themes(THEMES, "genetics")
    dot = spec_to_dot.build_dot(example_spec(), themes)
    assert 'fillcolor="#dbeafe"' in dot
    assert 'color="#2563eb"' in dot


def test_render_graphviz_missing_dot_error_is_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing dot executable should produce a clear error."""
    render_graphviz = load_module(RENDER_GRAPHVIZ, "render_graphviz_missing")
    monkeypatch.setattr(render_graphviz.shutil, "which", lambda _: None)
    with pytest.raises(RuntimeError, match="Graphviz 'dot' executable was not found"):
        render_graphviz.require_dot()


def test_render_graphviz_invalid_dot_error_is_clear(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Graphviz failures should report stderr clearly."""
    render_graphviz = load_module(RENDER_GRAPHVIZ, "render_graphviz_invalid")
    fake_dot = tmp_path / "dot"
    fake_dot.write_text("#!/bin/sh\necho invalid DOT >&2\nexit 1\n", encoding="utf-8")
    fake_dot.chmod(0o755)
    source = tmp_path / "bad.dot"
    source.write_text("not dot", encoding="utf-8")
    monkeypatch.setattr(render_graphviz.shutil, "which", lambda _: str(fake_dot))
    with pytest.raises(RuntimeError, match="invalid DOT"):
        render_graphviz.render_dot(source, tmp_path / "bad.svg")


def test_render_graphviz_svg_generation_and_expectations_with_fake_dot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Renderer should create SVG and validate expected text and edges."""
    render_graphviz = load_module(RENDER_GRAPHVIZ, "render_graphviz_fake")
    fake_dot = tmp_path / "dot"
    fake_dot.write_text(
        "#!/bin/sh\n"
        "out=''\n"
        "while [ \"$#\" -gt 0 ]; do\n"
        "  if [ \"$1\" = '-o' ]; then shift; out=\"$1\"; fi\n"
        "  shift\n"
        "done\n"
        "printf '%s\\n' '<svg xmlns=\"http://www.w3.org/2000/svg\"><text>Raw data</text><text>reviewed edge</text></svg>' > \"$out\"\n",
        encoding="utf-8",
    )
    fake_dot.chmod(0o755)
    dot_path = tmp_path / "workflow.dot"
    dot_path.write_text("digraph workflow {\n  raw -> schema;\n}\n", encoding="utf-8")
    svg_path = tmp_path / "workflow.svg"
    monkeypatch.setattr(render_graphviz.shutil, "which", lambda _: str(fake_dot))
    render_graphviz.render_dot(dot_path, svg_path)
    render_graphviz.validate_svg(svg_path)
    render_graphviz.require_text(svg_path, ["Raw data", "reviewed edge"])
    render_graphviz.require_edges(dot_path, ["raw:schema"])


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is not installed")
def test_render_graphviz_with_real_graphviz(tmp_path: Path) -> None:
    """Render an SVG with real Graphviz when available."""
    spec_to_dot = load_module(SPEC_TO_DOT, "spec_to_dot_real")
    render_graphviz = load_module(RENDER_GRAPHVIZ, "render_graphviz_real")
    dot_path = tmp_path / "workflow.dot"
    svg_path = tmp_path / "workflow.svg"
    dot_path.write_text(
        spec_to_dot.build_dot(example_spec(), spec_to_dot.load_themes(THEMES)),
        encoding="utf-8",
    )
    render_graphviz.render_dot(dot_path, svg_path)
    render_graphviz.validate_svg(svg_path)
    render_graphviz.require_edges(dot_path, ["raw:schema", "schema:report"])
