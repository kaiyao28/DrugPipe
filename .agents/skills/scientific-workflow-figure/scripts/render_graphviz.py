#!/usr/bin/env python3
"""Render Graphviz DOT to SVG and optionally PNG."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def require_dot() -> str:
    """Return the dot executable path or fail clearly."""
    dot = shutil.which("dot")
    if dot is None:
        raise RuntimeError("Graphviz 'dot' executable was not found on PATH")
    return dot


def render_dot(dot_path: str | Path, svg_path: str | Path, *, fmt: str = "svg") -> Path:
    """Render a DOT file with Graphviz."""
    dot = require_dot()
    source = Path(dot_path)
    output = Path(svg_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [dot, f"-T{fmt}", str(source), "-o", str(output)]
    result = subprocess.run(command, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"Graphviz failed:\n{result.stderr.strip()}")
    return output


def validate_svg(path: str | Path) -> ET.Element:
    """Validate SVG XML and return the root element."""
    root = ET.parse(path).getroot()
    if not root.tag.endswith("svg"):
        raise ValueError(f"{path} is not an SVG document")
    return root


def require_text(svg_path: str | Path, expected: list[str]) -> None:
    """Fail if expected visible text is not present in the SVG."""
    text = Path(svg_path).read_text(encoding="utf-8")
    missing = [value for value in expected if value not in text]
    if missing:
        raise ValueError(f"Expected text missing from SVG: {', '.join(missing)}")


def require_edges(dot_path: str | Path, expected: list[str]) -> None:
    """Fail if expected source:target edges are not present in DOT."""
    dot = Path(dot_path).read_text(encoding="utf-8")
    missing = []
    for value in expected:
        try:
            source, target = value.split(":", 1)
        except ValueError as error:
            raise ValueError(f"Expected edge must use source:target syntax: {value}") from error
        if f"{source} -> {target}" not in dot:
            missing.append(value)
    if missing:
        raise ValueError(f"Expected edges missing from DOT: {', '.join(missing)}")


def main() -> None:
    """Run the CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dot", help="Input DOT file")
    parser.add_argument("-o", "--output", required=True, help="Output SVG file")
    parser.add_argument("--png", help="Optional PNG preview output")
    parser.add_argument(
        "--expect-text",
        action="append",
        default=[],
        help="Text expected in the rendered SVG; may be repeated",
    )
    parser.add_argument(
        "--expect-edge",
        action="append",
        default=[],
        help="DOT edge expected as source:target; may be repeated",
    )
    args = parser.parse_args()

    try:
        render_dot(args.dot, args.output, fmt="svg")
        validate_svg(args.output)
        if args.expect_text:
            require_text(args.output, args.expect_text)
        if args.expect_edge:
            require_edges(args.dot, args.expect_edge)
        if args.png:
            render_dot(args.dot, args.png, fmt="png")
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
