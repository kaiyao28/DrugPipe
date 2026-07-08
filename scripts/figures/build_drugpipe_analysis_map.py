"""Build and validate the DrugPipe analysis-map SVG."""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from pathlib import Path


SVG_WIDTH = 1600
SVG_HEIGHT = 1000
SAFE_MARGIN = 40
MIN_GAP = 20

MODULE_WIDTH = 370
MODULE_HEIGHT = 86
MODULE_ROW_GAP = 24
MODULE_COL_GAP = 40
MODULE_X1 = 180
MODULE_X2 = MODULE_X1 + MODULE_WIDTH + MODULE_COL_GAP
MODULE_Y1 = 176

TITLE_FONT = 21
SUBTITLE_FONT = 16
TABLE_TITLE_FONT = 29
TABLE_SUBTITLE_FONT = 18
OUTPUT_TITLE_FONT = 23
OUTPUT_SUBTITLE_FONT = 16


@dataclass(frozen=True)
class Node:
    """A rectangular SVG layout object with text and semantic styling."""

    name: str
    x: float
    y: float
    width: float
    height: float
    title_lines: tuple[str, ...]
    subtitle_lines: tuple[str, ...]
    style: str
    title_class: str = "card-title"
    subtitle_class: str = "card-sub"
    pad_x: float = 32
    title_y_offset: float = 36
    subtitle_y_offset: float = 65
    line_height: float = 24
    radius: float = 20
    filter_id: str = "shadow"
    motif: str | None = None
    validate_text: bool = True
    group: str | None = None

    @property
    def right(self) -> float:
        """Return the node's right edge."""
        return self.x + self.width

    @property
    def bottom(self) -> float:
        """Return the node's bottom edge."""
        return self.y + self.height

    @property
    def usable_width(self) -> float:
        """Return the text-safe width inside the node."""
        return self.width - (2 * self.pad_x)


@dataclass(frozen=True)
class Connector:
    """A connector between two named nodes and named anchors."""

    source: str
    source_anchor: str
    target: str
    target_anchor: str
    kind: str = "straight"


def estimate_text_width(text: str, font_size: float, weight: str = "regular") -> float:
    """Estimate rendered SVG text width in pixels."""
    factor = 0.58 if weight == "bold" else 0.52
    wide_chars = sum(1 for char in text if char in "MW@%&")
    narrow_chars = sum(1 for char in text if char in "ilI.,:/ ")
    return (len(text) * font_size * factor) + (wide_chars * font_size * 0.12) - (
        narrow_chars * font_size * 0.10
    )


def anchor(node: Node, name: str) -> tuple[float, float]:
    """Return a named anchor coordinate derived from node geometry."""
    anchors = {
        "top": (node.x + node.width / 2, node.y),
        "bottom": (node.x + node.width / 2, node.bottom),
        "left": (node.x, node.y + node.height / 2),
        "right": (node.right, node.y + node.height / 2),
        "top_left": (node.x, node.y),
        "top_right": (node.right, node.y),
        "bottom_left": (node.x, node.bottom),
        "bottom_right": (node.right, node.bottom),
        "bottom_25": (node.x + node.width * 0.25, node.bottom),
        "bottom_50": (node.x + node.width * 0.50, node.bottom),
        "bottom_75": (node.x + node.width * 0.75, node.bottom),
    }
    if name not in anchors:
        raise ValueError(f"Unknown anchor '{name}' for node '{node.name}'")
    return anchors[name]


def draw_multiline_text(
    lines: tuple[str, ...],
    *,
    x: float,
    y: float,
    css_class: str,
    line_height: float,
) -> str:
    """Draw explicit SVG text lines without relying on automatic wrapping."""
    if not lines:
        return ""
    tspans = [
        f'<tspan x="{x:.0f}" dy="{0 if index == 0 else line_height:.0f}">'
        f"{escape(line)}</tspan>"
        for index, line in enumerate(lines)
    ]
    return f'<text class="{css_class}" x="{x:.0f}" y="{y:.0f}">{"".join(tspans)}</text>'


def draw_motif(node: Node) -> str:
    """Draw a small decorative motif inside a card when requested."""
    if node.motif is None:
        return ""
    right = node.right - 34
    mid_y = node.y + node.height / 2
    if node.motif == "dots":
        return "\n".join(
            [
                f'<circle class="tiny-dot" cx="{right - 18:.0f}" cy="{mid_y - 12:.0f}" r="5"/>',
                f'<circle class="tiny-dot" cx="{right - 40:.0f}" cy="{mid_y + 12:.0f}" r="4"/>',
            ]
        )
    if node.motif == "pip":
        y = mid_y + 6
        return (
            f'<path d="M{right - 54:.0f} {y:.0f} H{right - 8:.0f}" '
            'stroke="#0284c7" stroke-width="4" stroke-linecap="round" opacity="0.7"/>'
            f'<circle class="tiny-dot" cx="{right - 36:.0f}" cy="{y:.0f}" r="5"/>'
            f'<circle class="tiny-dot" cx="{right - 10:.0f}" cy="{y:.0f}" r="4"/>'
        )
    if node.motif == "bars":
        return "\n".join(
            [
                f'<rect x="{right - 66:.0f}" y="{mid_y - 10:.0f}" width="54" height="12" rx="6" fill="#0ea5e9" opacity="0.75"/>',
                f'<rect x="{right - 100:.0f}" y="{mid_y + 12:.0f}" width="82" height="12" rx="6" fill="#7dd3fc" opacity="0.85"/>',
            ]
        )
    if node.motif == "links":
        return (
            f'<circle class="tiny-dot" cx="{right - 62:.0f}" cy="{mid_y - 2:.0f}" r="5"/>'
            f'<circle class="tiny-dot" cx="{right - 36:.0f}" cy="{mid_y + 16:.0f}" r="5"/>'
            f'<path d="M{right - 62:.0f} {mid_y - 2:.0f} L{right - 36:.0f} {mid_y + 16:.0f} '
            f'L{right - 8:.0f} {mid_y - 6:.0f}" stroke="#0284c7" stroke-width="3" '
            'fill="none" stroke-linecap="round" opacity="0.7"/>'
        )
    if node.motif == "cells":
        return "\n".join(
            [
                f'<circle class="tiny-green" cx="{right - 58:.0f}" cy="{mid_y - 8:.0f}" r="5"/>',
                f'<circle class="tiny-green" cx="{right - 34:.0f}" cy="{mid_y + 8:.0f}" r="4"/>',
                f'<circle class="tiny-green" cx="{right - 10:.0f}" cy="{mid_y - 14:.0f}" r="4"/>',
            ]
        )
    if node.motif == "wave":
        return (
            f'<path d="M{right - 72:.0f} {mid_y - 4:.0f} C{right - 52:.0f} {mid_y - 28:.0f} '
            f'{right - 26:.0f} {mid_y + 24:.0f} {right - 4:.0f} {mid_y:.0f}" '
            'stroke="#16a34a" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.58"/>'
        )
    if node.motif == "arrow":
        return (
            f'<path d="M{right - 96:.0f} {mid_y + 5:.0f} H{right - 22:.0f}" '
            'stroke="#16a34a" stroke-width="4" stroke-linecap="round" opacity="0.72"/>'
            f'<path d="M{right - 34:.0f} {mid_y - 4:.0f} L{right - 20:.0f} {mid_y + 5:.0f} '
            f'L{right - 34:.0f} {mid_y + 14:.0f}" stroke="#16a34a" stroke-width="4" '
            'fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.72"/>'
        )
    if node.motif == "shield":
        return (
            f'<path d="M{right - 54:.0f} {mid_y - 25:.0f} L{right - 27:.0f} {mid_y - 12:.0f} '
            f'L{right:.0f} {mid_y - 25:.0f} V{mid_y - 1:.0f} '
            f'C{right:.0f} {mid_y + 18:.0f} {right - 14:.0f} {mid_y + 30:.0f} '
            f'{right - 27:.0f} {mid_y + 38:.0f} C{right - 40:.0f} {mid_y + 30:.0f} '
            f'{right - 54:.0f} {mid_y + 18:.0f} {right - 54:.0f} {mid_y - 1:.0f} Z" '
            'fill="#bbf7d0" stroke="#16a34a" stroke-width="2" opacity="0.9"/>'
        )
    if node.motif == "table":
        return "\n".join(
            [
                f'<rect x="{node.right - 138:.0f}" y="{node.y + 30:.0f}" width="86" height="10" rx="5" fill="#16a34a" opacity="0.72"/>',
                f'<rect x="{node.right - 174:.0f}" y="{node.y + 55:.0f}" width="122" height="10" rx="5" fill="#86efac" opacity="0.72"/>',
                f'<rect x="{node.right - 212:.0f}" y="{node.y + 80:.0f}" width="160" height="10" rx="5" fill="#bbf7d0" opacity="0.72"/>',
            ]
        )
    if node.motif == "dot-purple":
        return f'<circle class="tiny-purple" cx="{node.right - 42:.0f}" cy="{node.y + 32:.0f}" r="5"/>'
    return ""


def draw_card(node: Node) -> str:
    """Draw one SVG card from a node definition."""
    title = draw_multiline_text(
        node.title_lines,
        x=node.x + node.pad_x,
        y=node.y + node.title_y_offset,
        css_class=node.title_class,
        line_height=node.line_height,
    )
    subtitle = draw_multiline_text(
        node.subtitle_lines,
        x=node.x + node.pad_x,
        y=node.y + node.subtitle_y_offset,
        css_class=node.subtitle_class,
        line_height=node.line_height,
    )
    motif = draw_motif(node)
    return (
        f'<g filter="url(#{node.filter_id})" aria-label="{escape(node.name)}">\n'
        f'  <rect class="{node.style}" x="{node.x:.0f}" y="{node.y:.0f}" '
        f'width="{node.width:.0f}" height="{node.height:.0f}" rx="{node.radius:.0f}"/>\n'
        f"  {title}\n"
        f"  {subtitle}\n"
        f"  {motif}\n"
        "</g>"
    )


def draw_connector(connector: Connector, nodes: dict[str, Node]) -> str:
    """Draw a connector from named anchors derived from node geometry."""
    start = anchor(nodes[connector.source], connector.source_anchor)
    end = anchor(nodes[connector.target], connector.target_anchor)
    if connector.kind == "curve":
        control_y = (start[1] + end[1]) / 2
        path = f"M{start[0]:.0f} {start[1]:.0f} C{start[0]:.0f} {control_y:.0f} {end[0]:.0f} {control_y:.0f} {end[0]:.0f} {end[1]:.0f}"
    elif connector.kind == "orthogonal":
        mid_y = (start[1] + end[1]) / 2
        path = f"M{start[0]:.0f} {start[1]:.0f} V{mid_y:.0f} H{end[0]:.0f} V{end[1]:.0f}"
    else:
        path = f"M{start[0]:.0f} {start[1]:.0f} L{end[0]:.0f} {end[1]:.0f}"
    return f'<path class="flow" d="{path}"/>'


def validate_no_overlap(nodes: dict[str, Node], min_gap: float = MIN_GAP) -> None:
    """Fail if any validated cards overlap or are too close."""
    node_list = [node for node in nodes.values() if node.group != "decorative"]
    for index, first in enumerate(node_list):
        for second in node_list[index + 1 :]:
            separated = (
                first.right + min_gap <= second.x
                or second.right + min_gap <= first.x
                or first.bottom + min_gap <= second.y
                or second.bottom + min_gap <= first.y
            )
            if not separated:
                raise ValueError(f"Nodes overlap or are too close: {first.name}, {second.name}")


def validate_canvas_bounds(
    nodes: dict[str, Node],
    width: float = SVG_WIDTH,
    height: float = SVG_HEIGHT,
    margin: float = SAFE_MARGIN,
) -> None:
    """Fail if a card leaves the safe canvas area."""
    for node in nodes.values():
        if node.group == "decorative":
            continue
        if node.x < margin or node.y < margin or node.right > width - margin or node.bottom > height - margin:
            raise ValueError(f"Node '{node.name}' leaves the safe canvas area")


def validate_text_capacity(nodes: dict[str, Node]) -> None:
    """Fail if estimated text width exceeds card usable width."""
    class_sizes = {
        "card-title": (TITLE_FONT, "bold"),
        "card-sub": (SUBTITLE_FONT, "regular"),
        "table-title": (TABLE_TITLE_FONT, "bold"),
        "table-sub": (TABLE_SUBTITLE_FONT, "regular"),
        "output-title": (OUTPUT_TITLE_FONT, "bold"),
        "output-sub": (OUTPUT_SUBTITLE_FONT, "regular"),
        "note-title": (18, "bold"),
        "note": (15, "regular"),
    }
    for node in nodes.values():
        if not node.validate_text:
            continue
        for line in node.title_lines:
            font_size, weight = class_sizes[node.title_class]
            if estimate_text_width(line, font_size, weight) > node.usable_width:
                raise ValueError(f"Title text too wide for node '{node.name}': {line}")
        for line in node.subtitle_lines:
            font_size, weight = class_sizes[node.subtitle_class]
            if estimate_text_width(line, font_size, weight) > node.usable_width:
                raise ValueError(f"Subtitle text too wide for node '{node.name}': {line}")
        if node.title_lines and node.subtitle_lines:
            title_last_baseline = node.title_y_offset + (len(node.title_lines) - 1) * node.line_height
            if node.subtitle_y_offset - title_last_baseline < 22:
                raise ValueError(f"Title and subtitle text overlap in node '{node.name}'")
        last_baseline = 0.0
        if node.title_lines:
            last_baseline = max(
                last_baseline,
                node.title_y_offset + (len(node.title_lines) - 1) * node.line_height,
            )
        if node.subtitle_lines:
            last_baseline = max(
                last_baseline,
                node.subtitle_y_offset + (len(node.subtitle_lines) - 1) * node.line_height,
            )
        if last_baseline > node.height - 6:
            raise ValueError(f"Text block too tall for node '{node.name}'")


def validate_connectors(connectors: tuple[Connector, ...], nodes: dict[str, Node]) -> None:
    """Fail if connectors reference unknown nodes or anchors."""
    for connector in connectors:
        if connector.source not in nodes:
            raise ValueError(f"Unknown connector source: {connector.source}")
        if connector.target not in nodes:
            raise ValueError(f"Unknown connector target: {connector.target}")
        anchor(nodes[connector.source], connector.source_anchor)
        anchor(nodes[connector.target], connector.target_anchor)


def build_nodes() -> dict[str, Node]:
    """Return structured node geometry for the analysis map."""
    module_specs = [
        ("gwas", 0, 0, "GWAS QC + loci", "harmonisation / regions", "blue", "dots"),
        ("finemap", 1, 0, "Fine-mapping", "PIP / credible sets", "blue", "pip"),
        ("l2g", 0, 1, "Locus-to-gene", "candidate gene evidence", "blue", "bars"),
        ("qtl", 1, 1, "QTL / colocalisation", "molecular links", "blue", "links"),
        ("expression", 0, 2, "Expression + cell context", "PCA / groups / cell types", "green", None),
        ("pathways", 1, 2, "Pathways + enrichment", "biological mechanisms", "green", "wave"),
        ("mr", 0, 3, "MR target validation", "effect / direction evidence", "green", "arrow"),
        ("safety", 1, 3, "Safety + druggability", "liability / tractability", "green", "shield"),
    ]
    nodes = {
        name: Node(
            name=name,
            x=MODULE_X1 if col == 0 else MODULE_X2,
            y=MODULE_Y1 + row * (MODULE_HEIGHT + MODULE_ROW_GAP),
            width=MODULE_WIDTH,
            height=MODULE_HEIGHT,
            title_lines=(title,),
            subtitle_lines=(subtitle,),
            style=style,
            motif=motif,
            group="module",
        )
        for name, col, row, title, subtitle, style, motif in module_specs
    }
    nodes.update(
        {
            "note": Node(
                name="note",
                x=1030,
                y=176,
                width=400,
                height=160,
                title_lines=("Use the tools and data", "appropriate to each analysis"),
                subtitle_lines=(
                    "Established tools, public resources",
                    "or local analyses can produce each",
                    "module's reviewed summary outputs.",
                ),
                style="neutral",
                title_class="note-title",
                subtitle_class="note",
                title_y_offset=40,
                subtitle_y_offset=90,
                line_height=24,
                radius=24,
                filter_id="softShadow",
                group="note",
            ),
            "evidence_tables": Node(
                name="evidence_tables",
                x=300,
                y=642,
                width=1000,
                height=100,
                title_lines=("Standard evidence tables",),
                subtitle_lines=("documented schemas • reviewed outputs • reusable between analysis steps",),
                style="green",
                title_class="table-title",
                subtitle_class="table-sub",
                pad_x=58,
                title_y_offset=43,
                subtitle_y_offset=73,
                radius=26,
                motif="table",
                group="evidence",
            ),
            "figures": Node(
                name="figures",
                x=150,
                y=780,
                width=420,
                height=74,
                title_lines=("Standard figures",),
                subtitle_lines=("PCA / volcano / QQ / forest / heatmaps",),
                style="purple",
                title_class="output-title",
                subtitle_class="output-sub",
                title_y_offset=32,
                subtitle_y_offset=58,
                radius=22,
                filter_id="softShadow",
                motif="dot-purple",
                group="output",
            ),
            "target_integration": Node(
                name="target_integration",
                x=610,
                y=768,
                width=380,
                height=74,
                title_lines=("Target integration",),
                subtitle_lines=("combine evidence layers",),
                style="orange",
                title_class="output-title",
                subtitle_class="output-sub",
                title_y_offset=32,
                subtitle_y_offset=58,
                radius=22,
                group="output",
            ),
            "reports": Node(
                name="reports",
                x=1030,
                y=780,
                width=420,
                height=74,
                title_lines=("Interpretation + reports",),
                subtitle_lines=("guidance / target cards / Markdown",),
                style="orange",
                title_class="output-title",
                subtitle_class="output-sub",
                title_y_offset=32,
                subtitle_y_offset=58,
                radius=22,
                filter_id="softShadow",
                group="output",
            ),
            "ranked": Node(
                name="ranked",
                x=540,
                y=884,
                width=520,
                height=56,
                title_lines=("Ranked target hypotheses",),
                subtitle_lines=("prioritisation for follow-up",),
                style="orange",
                title_class="output-title",
                subtitle_class="output-sub",
                title_y_offset=25,
                subtitle_y_offset=47,
                radius=24,
                group="output",
            ),
        }
    )
    return nodes


def build_connectors() -> tuple[Connector, ...]:
    """Return connectors using named node anchors."""
    return (
        Connector("evidence_tables", "bottom_25", "figures", "top", "curve"),
        Connector("evidence_tables", "bottom_50", "target_integration", "top", "straight"),
        Connector("evidence_tables", "bottom_75", "reports", "top", "curve"),
        Connector("target_integration", "bottom", "ranked", "top", "straight"),
    )


def validate_layout(nodes: dict[str, Node], connectors: tuple[Connector, ...]) -> None:
    """Run all layout validations."""
    validate_no_overlap(nodes)
    validate_canvas_bounds(nodes)
    validate_text_capacity(nodes)
    validate_connectors(connectors, nodes)


def build_svg(nodes: dict[str, Node], connectors: tuple[Connector, ...]) -> str:
    """Build the SVG text from validated nodes and connectors."""
    module_grid_left = MODULE_X1 - 12
    module_grid_right = MODULE_X2 + MODULE_WIDTH + 12
    module_grid_bottom = MODULE_Y1 + 4 * MODULE_HEIGHT + 3 * MODULE_ROW_GAP + 28
    evidence = nodes["evidence_tables"]
    cards = "\n\n  ".join(draw_card(node) for node in nodes.values())
    connector_svg = "\n  ".join(draw_connector(connector, nodes) for connector in connectors)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">DrugPipe analysis map</title>
  <desc id="desc">A modular post-GWAS target-discovery analysis map showing independently accessible analysis modules, standard evidence tables, and reusable outputs for target integration, figures, reports and ranked hypotheses.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#f8fafc"/>
      <stop offset="1" stop-color="#eef2f7"/>
    </linearGradient>
    <linearGradient id="blueCard" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#dff3ff"/>
      <stop offset="1" stop-color="#f0f7ff"/>
    </linearGradient>
    <linearGradient id="greenCard" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#def7e8"/>
      <stop offset="1" stop-color="#f0fdf4"/>
    </linearGradient>
    <linearGradient id="neutralCard" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#f1f5f9"/>
      <stop offset="1" stop-color="#ffffff"/>
    </linearGradient>
    <linearGradient id="orangeCard" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#ffedd5"/>
      <stop offset="1" stop-color="#fff7ed"/>
    </linearGradient>
    <linearGradient id="purpleCard" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#ede9fe"/>
      <stop offset="1" stop-color="#f5f3ff"/>
    </linearGradient>
    <filter id="shadow" x="-14%" y="-18%" width="128%" height="140%">
      <feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#0f172a" flood-opacity="0.10"/>
    </filter>
    <filter id="softShadow" x="-12%" y="-15%" width="124%" height="132%">
      <feDropShadow dx="0" dy="7" stdDeviation="7" flood-color="#0f172a" flood-opacity="0.075"/>
    </filter>
    <marker id="arrow" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto">
      <path d="M0 0 L12 6 L0 12 Z" fill="#94a3b8"/>
    </marker>
    <style>
      .title {{ font: 800 40px Inter, Arial, sans-serif; fill: #0f172a; letter-spacing: 0; }}
      .subtitle {{ font: 20px Inter, Arial, sans-serif; fill: #475569; letter-spacing: 0; }}
      .zone {{ font: 800 14px Inter, Arial, sans-serif; fill: #64748b; letter-spacing: 1.5px; }}
      .note-title {{ font: 800 18px Inter, Arial, sans-serif; fill: #334155; letter-spacing: 0; }}
      .note {{ font: 15px Inter, Arial, sans-serif; fill: #64748b; letter-spacing: 0; }}
      .card-title {{ font: 800 {TITLE_FONT}px Inter, Arial, sans-serif; fill: #0f172a; letter-spacing: 0; }}
      .card-sub {{ font: {SUBTITLE_FONT}px Inter, Arial, sans-serif; fill: #475569; letter-spacing: 0; }}
      .table-title {{ font: 800 {TABLE_TITLE_FONT}px Inter, Arial, sans-serif; fill: #14532d; letter-spacing: 0; }}
      .table-sub {{ font: {TABLE_SUBTITLE_FONT}px Inter, Arial, sans-serif; fill: #166534; letter-spacing: 0; }}
      .output-title {{ font: 800 {OUTPUT_TITLE_FONT}px Inter, Arial, sans-serif; fill: #0f172a; letter-spacing: 0; }}
      .output-sub {{ font: {OUTPUT_SUBTITLE_FONT}px Inter, Arial, sans-serif; fill: #475569; letter-spacing: 0; }}
      .blue {{ fill: url(#blueCard); stroke: #0284c7; stroke-width: 2; }}
      .green {{ fill: url(#greenCard); stroke: #16a34a; stroke-width: 2; }}
      .neutral {{ fill: url(#neutralCard); stroke: #94a3b8; stroke-width: 1.6; }}
      .orange {{ fill: url(#orangeCard); stroke: #d97706; stroke-width: 2; }}
      .purple {{ fill: url(#purpleCard); stroke: #7c3aed; stroke-width: 2; }}
      .guide {{ stroke: #94a3b8; stroke-width: 2; fill: none; stroke-linecap: round; opacity: 0.38; }}
      .flow {{ stroke: #94a3b8; stroke-width: 2.6; fill: none; marker-end: url(#arrow); stroke-linecap: round; opacity: 0.88; }}
      .dash {{ stroke: #94a3b8; stroke-width: 2; fill: none; stroke-dasharray: 5 8; stroke-linecap: round; opacity: 0.42; }}
      .tiny-dot {{ fill: #0284c7; opacity: 0.8; }}
      .tiny-green {{ fill: #16a34a; opacity: 0.75; }}
      .tiny-purple {{ fill: #7c3aed; opacity: 0.72; }}
    </style>
  </defs>

  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" fill="url(#bg)"/>
  <path d="M80 200 C270 135 430 205 612 150 C820 88 1010 160 1190 110 C1336 70 1450 86 1520 130" fill="none" stroke="#dbeafe" stroke-width="38" opacity="0.42"/>
  <path d="M110 812 C306 762 478 848 688 794 C905 738 1092 784 1286 742 C1412 714 1490 724 1530 758" fill="none" stroke="#e9d5ff" stroke-width="32" opacity="0.34"/>

  <text class="title" x="70" y="66">DrugPipe analysis map</text>
  <text class="subtitle" x="70" y="104">Reusable analysis modules, standard evidence schemas and post-GWAS interpretation workflows.</text>

  <text class="zone" x="380" y="150">CHOOSE THE RELEVANT ANALYSIS MODULE</text>
  <text class="zone" x="1060" y="150">MODULAR INPUTS</text>

  {cards}

  <path class="guide" d="M{module_grid_left:.0f} {module_grid_bottom:.0f} H{module_grid_right:.0f}"/>
  <path class="guide" d="M{module_grid_left:.0f} {module_grid_bottom:.0f} C{module_grid_left:.0f} {module_grid_bottom + 24:.0f} {module_grid_left + 28:.0f} {module_grid_bottom + 34:.0f} {module_grid_left + 60:.0f} {module_grid_bottom + 34:.0f}"/>
  <path class="guide" d="M{module_grid_right:.0f} {module_grid_bottom:.0f} C{module_grid_right:.0f} {module_grid_bottom + 24:.0f} {module_grid_right - 28:.0f} {module_grid_bottom + 34:.0f} {module_grid_right - 60:.0f} {module_grid_bottom + 34:.0f}"/>
  <path class="dash" d="M{(module_grid_left + module_grid_right) / 2:.0f} {module_grid_bottom:.0f} V{evidence.y:.0f}"/>
  <text class="zone" x="648" y="632">STANDARD EVIDENCE LAYER</text>

  {connector_svg}
</svg>
"""
    return "\n".join(line.rstrip() for line in svg.splitlines()) + "\n"


def write_svg(path: str | Path = "docs/assets/drugpipe-workflow.svg") -> Path:
    """Validate and write the generated analysis-map SVG."""
    nodes = build_nodes()
    connectors = build_connectors()
    validate_layout(nodes, connectors)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_svg(nodes, connectors), encoding="utf-8")
    return output


def main() -> None:
    """Generate the DrugPipe analysis-map SVG."""
    output = write_svg()
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
