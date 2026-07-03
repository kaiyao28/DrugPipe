"""Generate per-target Markdown evidence cards."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def make_target_cards(
    results_dir: str | Path,
    outdir: str | Path,
    top_n: int = 10,
) -> dict[str, Any]:
    """Create Markdown evidence cards for the top ranked targets."""

    base_dir = Path(results_dir)
    output_dir = Path(outdir)

    ranked_targets = _read_required_tsv(base_dir / "targets" / "ranked_targets.tsv", "ranked targets")
    ranked_targets = sorted(ranked_targets, key=lambda row: _numeric(row.get("rank", "inf")))[:top_n]

    evidence = {
        "loci": _index_by(_read_optional_tsv(base_dir / "loci" / "loci.tsv"), "locus_id"),
        "gene_map": _index_by_pair(
            _read_optional_tsv(base_dir / "genes" / "locus_gene_map.tsv"),
            "gene_name",
            "locus_id",
        ),
        "finemap": _index_by(_read_optional_tsv(base_dir / "finemap" / "locus_finemap_summary.tsv"), "locus_id"),
        "coloc": _index_by(_read_optional_tsv(base_dir / "qtl" / "gene_coloc_summary.tsv"), "gene_name"),
        "cell": _index_by(_read_optional_tsv(base_dir / "cell_context" / "bone_cell_relevance.tsv"), "gene_name"),
        "pathway": _index_by(_read_optional_tsv(base_dir / "biology" / "gene_pathway_context.tsv"), "gene_name"),
        "mr": _index_by(_read_optional_tsv(base_dir / "mr" / "gene_mr_summary.tsv"), "gene_name"),
        "mediation": _index_by(_read_optional_tsv(base_dir / "mr" / "gene_mediation_summary.tsv"), "gene_name"),
        "phe": _index_by(_read_optional_tsv(base_dir / "mr" / "gene_phe_mr_safety_summary.tsv"), "gene_name"),
        "druggability": _index_by(_read_optional_tsv(base_dir / "targets" / "druggability.tsv"), "gene_name"),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    card_paths = []
    for target in ranked_targets:
        gene_name = target["gene_name"]
        card_path = output_dir / f"{_safe_filename(gene_name)}.md"
        card_path.write_text(_render_card(target, evidence), encoding="utf-8")
        card_paths.append(str(card_path))

    return {
        "target_card_paths": card_paths,
        "n_cards": len(card_paths),
    }


def _render_card(target: dict[str, str], evidence: dict[str, Any]) -> str:
    gene_name = target["gene_name"]
    locus_id = target.get("locus_id", "")
    locus = evidence["loci"].get(locus_id, {})
    gene_map = evidence["gene_map"].get((gene_name, locus_id), {})
    finemap = evidence["finemap"].get(locus_id, {})
    coloc = evidence["coloc"].get(gene_name, {})
    cell = evidence["cell"].get(gene_name, {})
    pathway = evidence["pathway"].get(gene_name, {})
    mr = evidence["mr"].get(gene_name, {})
    mediation = evidence["mediation"].get(gene_name, {})
    phe = evidence["phe"].get(gene_name, {})
    druggability = evidence["druggability"].get(gene_name, {})

    interpretation = _interpretation(target, phe, druggability)

    return "\n".join(
        [
            f"# Target: {gene_name}",
            "",
            "## Overall priority",
            f"- Rank: {_value(target, 'rank')}",
            f"- Target score: {_value(target, 'target_score')}",
            f"- One-sentence interpretation: {interpretation}",
            "",
            "## Genetic evidence",
            f"- locus_id: {_display(locus_id)}",
            f"- lead SNP if available: {_value(locus, 'LEAD_SNP')}",
            f"- genetic association score: {_value(target, 'genetic_association_score')}",
            f"- fine-mapping score: {_value(target, 'fine_mapping_score', finemap.get('locus_finemap_score', ''))}",
            "",
            "## Locus-to-gene evidence",
            f"- locus_to_gene_score: {_value(target, 'locus_to_gene_score', gene_map.get('locus_to_gene_score', ''))}",
            f"- evidence labels: {_value(gene_map, 'evidence_labels')}",
            f"- distance to TSS if available: {_value(gene_map, 'distance_to_tss')}",
            "",
            "## Molecular QTL evidence",
            f"- best qtl type: {_value(target, 'best_qtl_type', coloc.get('best_qtl_type', ''))}",
            f"- best tissue or cell: {_value(coloc, 'best_tissue_or_cell')}",
            f"- best PP_H4: {_value(coloc, 'max_pp_h4')}",
            f"- effect direction: {_value(target, 'best_effect_direction', coloc.get('best_effect_direction', ''))}",
            "",
            "## Bone-cell context",
            f"- top cell context: {_value(target, 'top_cell_context', cell.get('top_cell_context', ''))}",
            f"- osteoblast score: {_value(cell, 'osteoblast_score')}",
            f"- osteoclast score: {_value(cell, 'osteoclast_score')}",
            f"- osteocyte score: {_value(cell, 'osteocyte_score')}",
            "",
            "## Mechanism and pathway context",
            f"- relevant pathways: {_value(pathway, 'pathways')}",
            "",
            "## MR target-validation evidence",
            f"- best MR outcome: {_value(target, 'best_mr_outcome', mr.get('best_outcome', ''))}",
            f"- beta: {_value(mr, 'best_beta')}",
            f"- p-value: {_value(mr, 'best_p')}",
            f"- direction: {_value(mr, 'mr_direction')}",
            f"- instrument strength if available: {_value(mr, 'best_f_statistic')}",
            "",
            "## Mediation evidence",
            f"- best mediator: {_value(target, 'best_mediator', mediation.get('best_mediator', ''))}",
            f"- mediator category: {_value(mediation, 'best_mediator_category')}",
            f"- proportion mediated: {_value(mediation, 'best_proportion_mediated')}",
            "",
            "## Phe-MR and safety",
            f"- liability flags: {_value(phe, 'n_liability_flags')}",
            f"- strongest liability trait: {_value(phe, 'strongest_liability_trait')}",
            f"- safety penalty: {_value(target, 'phe_mr_safety_penalty', phe.get('phe_mr_safety_penalty', ''))}",
            "",
            "## Druggability",
            f"- target class: {_value(target, 'target_class', druggability.get('target_class', ''))}",
            f"- modality: {_value(druggability, 'tractability_modality')}",
            f"- known drug: {_value(target, 'known_drug', druggability.get('known_drug', ''))}",
            f"- known drug name: {_value(target, 'known_drug_name', druggability.get('known_drug_name', ''))}",
            "",
            "## Interpretation",
            interpretation,
            "",
        ]
    )


def _interpretation(
    target: dict[str, str],
    phe: dict[str, str],
    druggability: dict[str, str],
) -> str:
    gene_name = target["gene_name"]
    score = _numeric(target.get("target_score", "0"))
    safety_penalty = _numeric(target.get("phe_mr_safety_penalty", phe.get("phe_mr_safety_penalty", "0")))
    drug_score = _numeric(target.get("druggability_score", druggability.get("druggability_score", "0")))

    if score >= 0.5 and safety_penalty == 0:
        stance = "a strong target hypothesis"
    elif score >= 0.35:
        stance = "a plausible target hypothesis that needs follow-up"
    else:
        stance = "a lower-priority hypothesis based on current evidence"

    tractability = "with tractability support" if drug_score > 0 else "with limited tractability evidence"
    return f"{gene_name} is {stance} {tractability}; safety and mechanism evidence should be reviewed before experimental prioritisation."


def _read_required_tsv(path: Path, label: str) -> list[dict[str, str]]:
    if not path.exists():
        msg = f"Required {label} file does not exist: {path}"
        raise FileNotFoundError(msg)
    return _read_optional_tsv(path)


def _read_optional_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _index_by(rows: list[dict[str, str]], column: str) -> dict[str, dict[str, str]]:
    return {row[column]: row for row in rows if row.get(column)}


def _index_by_pair(
    rows: list[dict[str, str]],
    first: str,
    second: str,
) -> dict[tuple[str, str], dict[str, str]]:
    return {(row[first], row[second]): row for row in rows if row.get(first) and row.get(second)}


def _value(row: dict[str, str], key: str, fallback: str = "") -> str:
    return _display(row.get(key, fallback))


def _display(value: str) -> str:
    return str(value) if str(value).strip() else "not available"


def _numeric(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _safe_filename(value: str) -> str:
    safe = "".join(character if character.isalnum() or character in {"_", "-"} else "_" for character in value)
    return safe or "unknown_target"
