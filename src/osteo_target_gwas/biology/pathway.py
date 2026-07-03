"""Pathway and mechanism annotation for candidate genes."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

GENE_PATHWAY_CONTEXT_COLUMNS = [
    "gene_name",
    "pathways",
    "n_pathways",
    "pathway_context_score",
]

PATHWAY_SUMMARY_COLUMNS = [
    "pathway_name",
    "n_candidate_genes",
    "genes",
]


def annotate_pathway_context(
    gene_map_path: str | Path,
    gene_sets_path: str | Path,
    outdir: str | Path,
) -> dict[str, Any]:
    """Map candidate genes to pathways and write gene/pathway summaries."""

    gene_map_rows = _read_tsv(Path(gene_map_path), "locus-gene map")
    gene_set_rows = _read_tsv(Path(gene_sets_path), "pathway gene-set")
    gene_to_pathways = _gene_to_pathways(gene_set_rows)
    candidate_genes = sorted({row["gene_name"] for row in gene_map_rows})

    gene_context_rows = [
        _gene_context_row(gene_name, gene_to_pathways.get(gene_name, set()))
        for gene_name in candidate_genes
    ]
    pathway_summary_rows = _pathway_summary_rows(candidate_genes, gene_set_rows)

    output_dir = Path(outdir) / "biology"
    output_dir.mkdir(parents=True, exist_ok=True)
    gene_context_path = output_dir / "gene_pathway_context.tsv"
    pathway_summary_path = output_dir / "pathway_summary.tsv"

    _write_tsv(gene_context_path, gene_context_rows, GENE_PATHWAY_CONTEXT_COLUMNS)
    _write_tsv(pathway_summary_path, pathway_summary_rows, PATHWAY_SUMMARY_COLUMNS)

    return {
        "gene_pathway_context_path": str(gene_context_path),
        "pathway_summary_path": str(pathway_summary_path),
        "n_genes": len(gene_context_rows),
        "n_pathways": len(pathway_summary_rows),
    }


def _gene_to_pathways(gene_set_rows: list[dict[str, str]]) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = defaultdict(set)
    for row in gene_set_rows:
        mapping[row["gene_name"]].add(row["pathway_name"])
    return mapping


def _gene_context_row(gene_name: str, pathways: set[str]) -> dict[str, str]:
    ordered_pathways = sorted(pathways)
    n_pathways = len(ordered_pathways)
    score = min(1.0, n_pathways / 3)
    return {
        "gene_name": gene_name,
        "pathways": ";".join(ordered_pathways),
        "n_pathways": str(n_pathways),
        "pathway_context_score": _format_float(score),
    }


def _pathway_summary_rows(
    candidate_genes: list[str],
    gene_set_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    candidate_gene_set = set(candidate_genes)
    pathway_to_genes: dict[str, set[str]] = defaultdict(set)

    for row in gene_set_rows:
        gene_name = row["gene_name"]
        if gene_name in candidate_gene_set:
            pathway_to_genes[row["pathway_name"]].add(gene_name)

    rows = []
    for pathway_name, genes in sorted(pathway_to_genes.items()):
        ordered_genes = sorted(genes)
        rows.append(
            {
                "pathway_name": pathway_name,
                "n_candidate_genes": str(len(ordered_genes)),
                "genes": ";".join(ordered_genes),
            }
        )

    return rows


def _read_tsv(path: Path, label: str) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)

    if reader.fieldnames is None:
        msg = f"{label} file {path} is empty or has no header row"
        raise ValueError(msg)
    return rows


def _write_tsv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _format_float(value: float) -> str:
    return f"{value:.12g}"
