"""Variant-to-gene mapping for GWAS loci."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from osteo_target_gwas.genes.l2g_import import read_l2g_scores

LOCUS_GENE_COLUMNS = [
    "locus_id",
    "gene_id",
    "gene_name",
    "CHR",
    "gene_start",
    "gene_end",
    "tss",
    "nearest_gene",
    "distance_to_tss",
    "locus_overlap",
    "l2g_score",
    "locus_to_gene_score",
    "evidence_labels",
]


def map_variants_to_genes(
    loci_path: str | Path,
    genes_path: str | Path,
    outdir: str | Path,
    l2g_path: str | Path | None = None,
) -> dict[str, Any]:
    """Map overlapping and nearest genes to each GWAS locus."""

    loci = _read_tsv(Path(loci_path), "loci")
    genes = _read_tsv(Path(genes_path), "gene annotation")
    l2g_scores = read_l2g_scores(l2g_path)

    mappings = []
    for locus in loci:
        locus_genes = _candidate_genes_for_locus(locus, genes, l2g_scores)
        mappings.extend(_annotate_locus_gene_records(locus, locus_genes, l2g_scores))

    output_dir = Path(outdir) / "genes"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "locus_gene_map.tsv"
    _write_tsv(output_path, mappings, LOCUS_GENE_COLUMNS)

    return {
        "locus_gene_map_path": str(output_path),
        "n_loci": len(loci),
        "n_gene_links": len(mappings),
        "mappings": mappings,
    }


def _candidate_genes_for_locus(
    locus: dict[str, str],
    genes: list[dict[str, str]],
    l2g_scores: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, str]]:
    chromosome = _normalise_chromosome(locus["CHR"])
    start = int(locus["START"])
    end = int(locus["END"])
    lead_bp = int(locus["LEAD_BP"])

    same_chromosome_genes = [
        gene for gene in genes if _normalise_chromosome(gene["chr"]) == chromosome
    ]
    overlapping = [
        gene
        for gene in same_chromosome_genes
        if int(gene["start"]) <= end and int(gene["end"]) >= start
    ]

    nearest = min(
        same_chromosome_genes,
        key=lambda gene: abs(int(gene["tss"]) - lead_bp),
        default=None,
    )

    candidates = {(gene["gene_id"], gene["gene_name"]): gene for gene in overlapping}
    if nearest is not None:
        candidates[(nearest["gene_id"], nearest["gene_name"])] = nearest

    for l2g_locus_id, gene_name in l2g_scores:
        if l2g_locus_id != locus["locus_id"]:
            continue
        for gene in same_chromosome_genes:
            if gene["gene_name"] == gene_name:
                candidates[(gene["gene_id"], gene["gene_name"])] = gene

    return sorted(candidates.values(), key=lambda gene: (int(gene["tss"]), gene["gene_name"]))


def _annotate_locus_gene_records(
    locus: dict[str, str],
    genes: list[dict[str, str]],
    l2g_scores: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, str]]:
    if not genes:
        return []

    lead_bp = int(locus["LEAD_BP"])
    nearest_gene_name = min(genes, key=lambda gene: abs(int(gene["tss"]) - lead_bp))["gene_name"]
    records = []

    for gene in genes:
        distance_to_tss = abs(int(gene["tss"]) - lead_bp)
        nearest_gene = gene["gene_name"] == nearest_gene_name
        locus_overlap = _gene_overlaps_locus(gene, locus)
        l2g = l2g_scores.get((locus["locus_id"], gene["gene_name"]), {})
        l2g_score = float(l2g.get("l2g_score", 0.0))
        score = 0.4 * float(nearest_gene) + 0.3 * float(locus_overlap) + 0.3 * l2g_score
        labels = _evidence_labels(nearest_gene, locus_overlap, l2g)

        records.append(
            {
                "locus_id": locus["locus_id"],
                "gene_id": gene["gene_id"],
                "gene_name": gene["gene_name"],
                "CHR": _normalise_chromosome(gene["chr"]),
                "gene_start": gene["start"],
                "gene_end": gene["end"],
                "tss": gene["tss"],
                "nearest_gene": str(nearest_gene).lower(),
                "distance_to_tss": str(distance_to_tss),
                "locus_overlap": str(locus_overlap).lower(),
                "l2g_score": _format_float(l2g_score),
                "locus_to_gene_score": _format_float(score),
                "evidence_labels": ";".join(labels),
            }
        )

    return records


def _gene_overlaps_locus(gene: dict[str, str], locus: dict[str, str]) -> bool:
    return int(gene["start"]) <= int(locus["END"]) and int(gene["end"]) >= int(locus["START"])


def _evidence_labels(
    nearest_gene: bool,
    locus_overlap: bool,
    l2g: dict[str, str],
) -> list[str]:
    labels = []
    if nearest_gene:
        labels.append("nearest_gene")
    if locus_overlap:
        labels.append("locus_overlap")
    if l2g:
        labels.append("l2g")
    return labels


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


def _normalise_chromosome(chromosome: str) -> str:
    return str(chromosome).upper().removeprefix("CHR")


def _format_float(value: float) -> str:
    return f"{value:.12g}"
