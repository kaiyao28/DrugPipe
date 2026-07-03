"""Integrated target scoring across post-GWAS evidence layers."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

from osteo_target_gwas.config import get_scoring_weights, load_default_config

RANKED_TARGET_COLUMNS = [
    "rank",
    "gene_name",
    "locus_id",
    "target_score",
    "genetic_association_score",
    "fine_mapping_score",
    "locus_to_gene_score",
    "qtl_colocalisation_score",
    "bone_cell_context_score",
    "pathway_context_score",
    "mr_target_validation_score",
    "mediation_score",
    "druggability_score",
    "phe_mr_safety_penalty",
    "annotation_bias_penalty",
    "top_cell_context",
    "best_qtl_type",
    "best_effect_direction",
    "best_mr_outcome",
    "best_mediator",
    "target_class",
    "known_drug",
    "known_drug_name",
    "evidence_summary",
]


def score_targets(
    results_dir: str | Path,
    config_path: str | Path = "config/default.yaml",
) -> dict[str, Any]:
    """Join evidence layers and write ranked target scores."""

    base_dir = Path(results_dir)
    config = load_default_config(config_path)
    weights = get_scoring_weights(config)

    gene_map_rows = _read_required_tsv(base_dir / "genes" / "locus_gene_map.tsv", "locus-gene map")
    loci_by_id = _index_by(_read_optional_tsv(base_dir / "loci" / "loci.tsv"), "locus_id")
    finemap_by_locus = _index_by(
        _read_optional_tsv(base_dir / "finemap" / "locus_finemap_summary.tsv"),
        "locus_id",
    )
    coloc_by_gene = _index_by(_read_optional_tsv(base_dir / "qtl" / "gene_coloc_summary.tsv"), "gene_name")
    cell_by_gene = _index_by(
        _read_optional_tsv(base_dir / "cell_context" / "bone_cell_relevance.tsv"),
        "gene_name",
    )
    pathway_by_gene = _index_by(
        _read_optional_tsv(base_dir / "biology" / "gene_pathway_context.tsv"),
        "gene_name",
    )
    mr_by_gene = _index_by(_read_optional_tsv(base_dir / "mr" / "gene_mr_summary.tsv"), "gene_name")
    mediation_by_gene = _index_by(
        _read_optional_tsv(base_dir / "mr" / "gene_mediation_summary.tsv"),
        "gene_name",
    )
    phe_by_gene = _index_by(
        _read_optional_tsv(base_dir / "mr" / "gene_phe_mr_safety_summary.tsv"),
        "gene_name",
    )
    druggability_by_gene = _index_by(
        _read_optional_tsv(base_dir / "targets" / "druggability.tsv"),
        "gene_name",
    )

    scored_rows = []
    for row in gene_map_rows:
        scored_rows.append(
            _score_gene_locus(
                row=row,
                weights=weights,
                loci_by_id=loci_by_id,
                finemap_by_locus=finemap_by_locus,
                coloc_by_gene=coloc_by_gene,
                cell_by_gene=cell_by_gene,
                pathway_by_gene=pathway_by_gene,
                mr_by_gene=mr_by_gene,
                mediation_by_gene=mediation_by_gene,
                phe_by_gene=phe_by_gene,
                druggability_by_gene=druggability_by_gene,
            )
        )

    scored_rows.sort(
        key=lambda row: (-float(row["target_score"]), row["gene_name"], row["locus_id"])
    )
    for rank, row in enumerate(scored_rows, start=1):
        row["rank"] = str(rank)

    output_dir = base_dir / "targets"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "ranked_targets.tsv"
    _write_tsv(output_path, scored_rows, RANKED_TARGET_COLUMNS)

    return {
        "ranked_targets_path": str(output_path),
        "n_targets": len(scored_rows),
        "targets": scored_rows,
    }


def _score_gene_locus(
    row: dict[str, str],
    weights: dict[str, float],
    loci_by_id: dict[str, dict[str, str]],
    finemap_by_locus: dict[str, dict[str, str]],
    coloc_by_gene: dict[str, dict[str, str]],
    cell_by_gene: dict[str, dict[str, str]],
    pathway_by_gene: dict[str, dict[str, str]],
    mr_by_gene: dict[str, dict[str, str]],
    mediation_by_gene: dict[str, dict[str, str]],
    phe_by_gene: dict[str, dict[str, str]],
    druggability_by_gene: dict[str, dict[str, str]],
) -> dict[str, str]:
    gene_name = row["gene_name"]
    locus_id = row["locus_id"]
    locus = loci_by_id.get(locus_id, {})
    finemap = finemap_by_locus.get(locus_id, {})
    coloc = coloc_by_gene.get(gene_name, {})
    cell = cell_by_gene.get(gene_name, {})
    pathway = pathway_by_gene.get(gene_name, {})
    mr = mr_by_gene.get(gene_name, {})
    mediation = mediation_by_gene.get(gene_name, {})
    phe = phe_by_gene.get(gene_name, {})
    druggability = druggability_by_gene.get(gene_name, {})

    genetic_association_score = _genetic_association_score(locus.get("LEAD_P", ""))
    fine_mapping_score = _float_or_zero(finemap.get("locus_finemap_score", "0"))
    locus_to_gene_score = _float_or_zero(row.get("locus_to_gene_score", "0"))
    qtl_colocalisation_score = _float_or_zero(coloc.get("qtl_colocalisation_score", "0"))
    bone_cell_context_score = _float_or_zero(cell.get("bone_cell_context_score", "0"))
    pathway_context_score = _float_or_zero(pathway.get("pathway_context_score", "0"))
    mr_target_validation_score = _float_or_zero(mr.get("mr_target_validation_score", "0"))
    mediation_score = _float_or_zero(mediation.get("mediation_score", "0"))
    druggability_score = _float_or_zero(druggability.get("druggability_score", "0"))
    phe_mr_safety_penalty = _float_or_zero(phe.get("phe_mr_safety_penalty", "0"))
    annotation_bias_penalty = _annotation_bias_penalty(pathway)

    target_score = (
        genetic_association_score * weights.get("genetic_association", 0.0)
        + fine_mapping_score * weights.get("fine_mapping", 0.0)
        + locus_to_gene_score * weights.get("locus_to_gene", 0.0)
        + qtl_colocalisation_score * weights.get("qtl_colocalisation", 0.0)
        + bone_cell_context_score * weights.get("bone_cell_context", 0.0)
        + pathway_context_score * weights.get("pathway_context", 0.0)
        + mr_target_validation_score * weights.get("mr_target_validation", 0.0)
        + druggability_score * weights.get("druggability", 0.0)
        + mediation_score * 0.05
        - phe_mr_safety_penalty
        - annotation_bias_penalty
    )

    return {
        "rank": "",
        "gene_name": gene_name,
        "locus_id": locus_id,
        "target_score": _format_float(target_score),
        "genetic_association_score": _format_float(genetic_association_score),
        "fine_mapping_score": _format_float(fine_mapping_score),
        "locus_to_gene_score": _format_float(locus_to_gene_score),
        "qtl_colocalisation_score": _format_float(qtl_colocalisation_score),
        "bone_cell_context_score": _format_float(bone_cell_context_score),
        "pathway_context_score": _format_float(pathway_context_score),
        "mr_target_validation_score": _format_float(mr_target_validation_score),
        "mediation_score": _format_float(mediation_score),
        "druggability_score": _format_float(druggability_score),
        "phe_mr_safety_penalty": _format_float(phe_mr_safety_penalty),
        "annotation_bias_penalty": _format_float(annotation_bias_penalty),
        "top_cell_context": cell.get("top_cell_context", "unknown") or "unknown",
        "best_qtl_type": coloc.get("best_qtl_type", ""),
        "best_effect_direction": coloc.get("best_effect_direction", ""),
        "best_mr_outcome": mr.get("best_outcome", ""),
        "best_mediator": mediation.get("best_mediator", ""),
        "target_class": druggability.get("target_class", ""),
        "known_drug": druggability.get("known_drug", "false"),
        "known_drug_name": druggability.get("known_drug_name", ""),
        "evidence_summary": _evidence_summary(
            genetic_association_score=genetic_association_score,
            fine_mapping_score=fine_mapping_score,
            qtl_colocalisation_score=qtl_colocalisation_score,
            bone_cell_context_score=bone_cell_context_score,
            mr_target_validation_score=mr_target_validation_score,
            druggability_score=druggability_score,
            phe_mr_safety_penalty=phe_mr_safety_penalty,
        ),
    }


def _genetic_association_score(lead_p: str) -> float:
    p_value = _float_or_zero(lead_p)
    if p_value <= 0:
        return 0.0
    return min(50.0, -math.log10(p_value)) / 50.0


def _annotation_bias_penalty(pathway: dict[str, str]) -> float:
    n_pathways = int(_float_or_zero(pathway.get("n_pathways", "0")))
    return 0.02 if n_pathways > 5 else 0.0


def _evidence_summary(
    genetic_association_score: float,
    fine_mapping_score: float,
    qtl_colocalisation_score: float,
    bone_cell_context_score: float,
    mr_target_validation_score: float,
    druggability_score: float,
    phe_mr_safety_penalty: float,
) -> str:
    labels = []
    if genetic_association_score > 0:
        labels.append("genetic association")
    if fine_mapping_score > 0:
        labels.append("fine-mapping")
    if qtl_colocalisation_score > 0:
        labels.append("QTL colocalisation")
    if bone_cell_context_score > 0:
        labels.append("bone-cell context")
    if mr_target_validation_score > 0:
        labels.append("MR support")
    if druggability_score > 0:
        labels.append("druggability")
    if phe_mr_safety_penalty > 0:
        labels.append("safety signal")
    return "; ".join(labels) if labels else "no supporting evidence available"


def _read_required_tsv(path: Path, label: str) -> list[dict[str, str]]:
    if not path.exists():
        msg = f"Required {label} file does not exist: {path}"
        raise FileNotFoundError(msg)
    return _read_tsv(path)


def _read_optional_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return _read_tsv(path)


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader)


def _index_by(rows: list[dict[str, str]], column: str) -> dict[str, dict[str, str]]:
    return {row[column]: row for row in rows if row.get(column)}


def _write_tsv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _float_or_zero(value: str | None) -> float:
    try:
        return float(value) if value not in (None, "") else 0.0
    except (TypeError, ValueError):
        return 0.0


def _format_float(value: float) -> str:
    return f"{value:.12g}"
