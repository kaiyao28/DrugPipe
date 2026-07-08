#!/usr/bin/env python3
"""Convert a semantic workflow YAML specification to Graphviz DOT."""

from __future__ import annotations

import argparse
import re
from html import escape as html_escape
from pathlib import Path
from typing import Any

import yaml


ID_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

PATTERN_SETTINGS = {
    "linear": {"splines": "polyline"},
    "branched": {"splines": "ortho"},
    "convergent": {"splines": "ortho"},
    "modular": {"splines": "ortho"},
    "layered": {"splines": "ortho"},
    "cyclic": {"splines": "polyline"},
}

DEFAULT_THEMES = {
    "input": {"fill": "#e0f2fe", "border": "#0284c7", "text": "#0f172a"},
    "analysis": {"fill": "#dcfce7", "border": "#16a34a", "text": "#0f172a"},
    "biology": {"fill": "#ecfdf5", "border": "#15803d", "text": "#0f172a"},
    "integration": {"fill": "#fffbeb", "border": "#d97706", "text": "#0f172a"},
    "output": {"fill": "#f5f3ff", "border": "#7c3aed", "text": "#0f172a"},
    "neutral": {"fill": "#f1f5f9", "border": "#64748b", "text": "#334155"},
}

DEFAULT_GRAPH = {
    "bgcolor": "#f8fafc",
    "fontname": "Arial",
    "nodesep": "0.55",
    "ranksep": "0.75",
    "splines": "ortho",
}

DEFAULT_NODE = {
    "shape": "rect",
    "style": "rounded,filled",
    "penwidth": "1.8",
    "margin": "0.16,0.10",
    "fontname": "Arial",
    "fontsize": "13",
}

DEFAULT_EDGE = {
    "color": "#94a3b8",
    "penwidth": "1.8",
    "arrowsize": "0.8",
    "fontname": "Arial",
    "fontsize": "11",
}


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML file and return a mapping."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def load_themes(path: str | Path | None, theme_set: str = "scientific-default") -> dict[str, Any]:
    """Load theme configuration with defaults."""
    if path is None:
        return {
            "themes": DEFAULT_THEMES,
            "defaults": {"graph": DEFAULT_GRAPH, "node": DEFAULT_NODE, "edge": DEFAULT_EDGE},
        }
    data = load_yaml(path)
    if "theme_sets" in data:
        theme_sets = data["theme_sets"]
        if theme_set not in theme_sets:
            raise ValueError(f"Unknown theme set '{theme_set}'")
        raw_themes = theme_sets[theme_set]
    else:
        raw_themes = data.get("themes", {})
    themes = {**DEFAULT_THEMES, **raw_themes}
    defaults = {
        "graph": {**DEFAULT_GRAPH, **data.get("defaults", {}).get("graph", {})},
        "node": {**DEFAULT_NODE, **data.get("defaults", {}).get("node", {})},
        "edge": {**DEFAULT_EDGE, **data.get("defaults", {}).get("edge", {})},
    }
    return {"themes": themes, "defaults": defaults}


def dot_id(value: str) -> str:
    """Return a safe DOT identifier."""
    if not ID_RE.match(value):
        raise ValueError(f"Invalid ID '{value}'. Use letters, digits and underscores.")
    return value


def esc(value: Any) -> str:
    """Escape a value for DOT quoted strings."""
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def html_label(title: str, subtitle: str | None = None) -> str:
    """Return a Graphviz HTML-like label."""
    title_html = html_escape(title)
    if not subtitle:
        return f'<<B>{title_html}</B>>'
    subtitle_html = html_escape(subtitle)
    return f'<<B>{title_html}</B><BR/><FONT POINT-SIZE="10">{subtitle_html}</FONT>>'


def validate_spec(spec: dict[str, Any]) -> None:
    """Validate workflow spec IDs, edges and groups."""
    nodes = spec.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("Spec must contain a non-empty 'nodes' list")
    node_ids: list[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("Each node must be a mapping")
        node_id = node.get("id")
        if not isinstance(node_id, str):
            raise ValueError("Each node must include a string id")
        dot_id(node_id)
        node_ids.append(node_id)
        if not node.get("title"):
            raise ValueError(f"Node '{node_id}' must include a title")
    duplicates = sorted({node_id for node_id in node_ids if node_ids.count(node_id) > 1})
    if duplicates:
        raise ValueError(f"Duplicate node IDs: {', '.join(duplicates)}")

    node_set = set(node_ids)
    for edge in spec.get("edges", []):
        if not isinstance(edge, dict):
            raise ValueError("Each edge must be a mapping")
        source = edge.get("source")
        target = edge.get("target")
        if source not in node_set:
            raise ValueError(f"Unknown edge source: {source}")
        if target not in node_set:
            raise ValueError(f"Unknown edge target: {target}")

    group_ids: list[str] = []
    for group in spec.get("groups", []):
        if not isinstance(group, dict):
            raise ValueError("Each group must be a mapping")
        group_id = group.get("id")
        if not isinstance(group_id, str):
            raise ValueError("Each group must include a string id")
        dot_id(group_id)
        group_ids.append(group_id)
        for node_id in group.get("nodes", []):
            if node_id not in node_set:
                raise ValueError(f"Group '{group_id}' references unknown node: {node_id}")
    duplicate_groups = sorted({group_id for group_id in group_ids if group_ids.count(group_id) > 1})
    if duplicate_groups:
        raise ValueError(f"Duplicate group IDs: {', '.join(duplicate_groups)}")


def attrs_to_dot(attrs: dict[str, Any]) -> str:
    """Render DOT attributes."""
    return ", ".join(f'{key}="{esc(value)}"' for key, value in attrs.items())


def build_dot(spec: dict[str, Any], theme_config: dict[str, Any]) -> str:
    """Build DOT from a validated workflow spec."""
    validate_spec(spec)
    figure = spec.get("figure", {})
    pattern = figure.get("pattern", "linear")
    direction = figure.get("direction", "LR")
    graph_attrs = {**theme_config["defaults"]["graph"], **PATTERN_SETTINGS.get(pattern, {})}
    graph_attrs["rankdir"] = direction
    graph_attrs["label"] = "\\n".join(
        part for part in [figure.get("title", ""), figure.get("subtitle", "")] if part
    )
    graph_attrs["labelloc"] = "t"
    graph_attrs["fontsize"] = "22"
    node_defaults = theme_config["defaults"]["node"]
    edge_defaults = theme_config["defaults"]["edge"]
    themes = theme_config["themes"]

    lines = ["digraph workflow {"]
    lines.append(f"  graph [{attrs_to_dot(graph_attrs)}];")
    lines.append(f"  node [{attrs_to_dot(node_defaults)}];")
    lines.append(f"  edge [{attrs_to_dot(edge_defaults)}];")

    grouped_nodes = {node_id for group in spec.get("groups", []) for node_id in group.get("nodes", [])}
    nodes_by_id = {node["id"]: node for node in spec["nodes"]}

    for group in spec.get("groups", []):
        group_id = dot_id(group["id"])
        lines.append(f"  subgraph cluster_{group_id} {{")
        lines.append(f'    label="{esc(group.get("label", group_id))}";')
        lines.append('    color="#cbd5e1";')
        lines.append('    style="rounded";')
        if group.get("rank"):
            lines.append(f'    rank="{esc(group["rank"])}";')
        for node_id in group.get("nodes", []):
            lines.append(f"    {render_node(nodes_by_id[node_id], themes)}")
        lines.append("  }")

    for node in spec["nodes"]:
        if node["id"] not in grouped_nodes:
            lines.append(f"  {render_node(node, themes)}")

    for edge in spec.get("edges", []):
        if edge.get("visible", True) is False:
            continue
        attrs = {}
        if edge.get("label"):
            attrs["label"] = edge["label"]
        if edge.get("constraint") is not None:
            attrs["constraint"] = str(bool(edge["constraint"])).lower()
        attr_text = f" [{attrs_to_dot(attrs)}]" if attrs else ""
        lines.append(f"  {dot_id(edge['source'])} -> {dot_id(edge['target'])}{attr_text};")

    same_rank_groups = [group for group in spec.get("groups", []) if group.get("rank") == "same"]
    for group in same_rank_groups:
        ranked = " ".join(dot_id(node_id) for node_id in group.get("nodes", []))
        if ranked:
            lines.append(f"  {{ rank=same; {ranked}; }}")

    lines.append("}")
    return "\n".join(lines) + "\n"


def render_node(node: dict[str, Any], themes: dict[str, dict[str, str]]) -> str:
    """Render one DOT node."""
    theme = themes.get(node.get("theme", "analysis"), themes["analysis"])
    attrs = {
        "fillcolor": theme["fill"],
        "color": theme["border"],
        "fontcolor": theme["text"],
    }
    return f"{dot_id(node['id'])} [label={html_label(node['title'], node.get('subtitle'))}, {attrs_to_dot(attrs)}];"


def main() -> None:
    """Run the CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", help="Workflow YAML specification")
    parser.add_argument("-o", "--output", required=True, help="Output DOT path")
    parser.add_argument("--themes", help="Optional themes.yaml path")
    parser.add_argument("--theme-set", default="scientific-default", help="Theme set name")
    args = parser.parse_args()

    spec = load_yaml(args.spec)
    theme_config = load_themes(args.themes, args.theme_set)
    dot = build_dot(spec, theme_config)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(dot, encoding="utf-8")


if __name__ == "__main__":
    main()
