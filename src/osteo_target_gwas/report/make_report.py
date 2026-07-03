"""Markdown report generation for target prioritisation runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

TOP_LOCI_COLUMNS = ["locus_id", "CHR", "START", "END", "LEAD_SNP", "LEAD_P", "N_SIGNIFICANT_VARIANTS"]
TOP_TARGET_COLUMNS = ["rank", "gene_name", "locus_id", "target_score", "evidence_summary"]
TOP_MR_COLUMNS = ["gene_name", "best_outcome", "best_p", "best_f_statistic", "mr_target_validation_score"]
TOP_SAFETY_COLUMNS = [
    "gene_name",
    "n_liability_flags",
    "strongest_liability_trait",
    "strongest_liability_p",
    "phe_mr_safety_penalty",
]


def make_markdown_report(
    results_dir: str | Path,
    out_path: str | Path,
) -> dict[str, Any]:
    """Create a Markdown report from available pipeline outputs."""

    base_dir = Path(results_dir)
    output_path = Path(out_path)

    qc_summary = _read_optional_json(base_dir / "qc" / "qc_summary.json")
    loci = _read_optional_tsv(base_dir / "loci" / "loci.tsv")
    gene_map = _read_optional_tsv(base_dir / "genes" / "locus_gene_map.tsv")
    finemap = _read_optional_tsv(base_dir / "finemap" / "locus_finemap_summary.tsv")
    coloc = _read_optional_tsv(base_dir / "qtl" / "gene_coloc_summary.tsv")
    cell_context = _read_optional_tsv(base_dir / "cell_context" / "bone_cell_relevance.tsv")
    pathway_summary = _read_optional_tsv(base_dir / "biology" / "pathway_summary.tsv")
    mr_summary = _read_optional_tsv(base_dir / "mr" / "gene_mr_summary.tsv")
    mediation_summary = _read_optional_tsv(base_dir / "mr" / "gene_mediation_summary.tsv")
    phe_summary = _read_optional_tsv(base_dir / "mr" / "gene_phe_mr_safety_summary.tsv")
    druggability = _read_optional_tsv(base_dir / "targets" / "druggability.tsv")
    ranked_targets = _read_optional_tsv(base_dir / "targets" / "ranked_targets.tsv")

    lines = [
        "# Target Prioritisation Report",
        "",
        "## 1. Run summary",
        "",
        f"- Results directory: `{base_dir}`",
        f"- Ranked targets: {len(ranked_targets)}",
        f"- Significant loci: {len(loci)}",
        f"- Candidate gene links: {len(gene_map)}",
        "",
        "## 2. GWAS QC summary",
        "",
        _qc_summary_text(qc_summary),
        "",
        "## 3. Significant loci",
        "",
        _markdown_table(_top_rows(loci, "LEAD_P", 10), TOP_LOCI_COLUMNS),
        "",
        "## 4. Candidate genes",
        "",
        f"{len({row.get('gene_name', '') for row in gene_map if row.get('gene_name')})} unique candidate genes from {len(gene_map)} locus-gene links.",
        "",
        "## 5. Fine-mapping evidence",
        "",
        _availability_text(finemap, "fine-mapping locus summaries"),
        "",
        "## 6. QTL colocalisation evidence",
        "",
        _availability_text(coloc, "gene-level QTL colocalisation summaries"),
        "",
        "## 7. Bone-cell context",
        "",
        _availability_text(cell_context, "bone-cell context rows"),
        "",
        "## 8. Pathway and mechanism interpretation",
        "",
        _availability_text(pathway_summary, "pathway summaries"),
        "",
        "## 9. MR target-validation evidence",
        "",
        _markdown_table(_top_rows(mr_summary, "mr_target_validation_score", 10, reverse=True), TOP_MR_COLUMNS),
        "",
        "## 10. Mediation MR evidence",
        "",
        _availability_text(mediation_summary, "gene mediation summaries"),
        "",
        "## 11. Phe-MR and safety scan",
        "",
        _markdown_table(_top_rows(phe_summary, "phe_mr_safety_penalty", 10, reverse=True), TOP_SAFETY_COLUMNS),
        "",
        "## 12. Druggability and tractability",
        "",
        _availability_text(druggability, "druggability annotations"),
        "",
        "## 13. Top ranked targets",
        "",
        _markdown_table(_top_rows(ranked_targets, "rank", 20), TOP_TARGET_COLUMNS),
        "",
        "## 14. Interpretation and caveats",
        "",
        "- This report summarises synthetic or precomputed evidence and does not perform new fine-mapping, colocalisation, or MR estimation.",
        "- Missing evidence layers are treated as unavailable rather than negative evidence.",
        "- Scores are intended for triage and should be followed by manual review and sensitivity analyses.",
        "",
        "## 15. Recommended next analyses",
        "",
        "- Re-run locus definition and fine-mapping with ancestry-matched LD reference data.",
        "- Validate colocalisation with tissue- and cell-type matched QTL resources.",
        "- Review MR instrument validity, pleiotropy, and sample overlap.",
        "- Inspect safety signals and tractability evidence before experimental prioritisation.",
        "",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "report_path": str(output_path),
        "n_ranked_targets": len(ranked_targets),
    }


def _qc_summary_text(summary: dict[str, Any]) -> str:
    if not summary:
        return "GWAS QC summary is not available yet."

    return "\n".join(
        [
            f"- Input variants: {summary.get('n_input_variants', 'NA')}",
            f"- Output variants: {summary.get('n_output_variants', 'NA')}",
            f"- Removed low INFO: {summary.get('n_removed_low_info', 'NA')}",
            f"- Removed low MAF: {summary.get('n_removed_low_maf', 'NA')}",
            f"- Removed missing effect fields: {summary.get('n_removed_missing', 'NA')}",
            f"- Removed ambiguous SNPs: {summary.get('n_removed_ambiguous', 'NA')}",
            f"- Minimum P-value: {summary.get('min_p', 'NA')}",
            f"- Genome-wide significant variants: {summary.get('n_genome_wide_significant', 'NA')}",
        ]
    )


def _availability_text(rows: list[dict[str, str]], label: str) -> str:
    if not rows:
        return f"{label.capitalize()} are not available yet."
    return f"{len(rows)} {label} available."


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    if not rows:
        return "Not available yet."

    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join(_escape_cell(row.get(column, "")) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, separator, *body])


def _top_rows(
    rows: list[dict[str, str]],
    sort_column: str,
    limit: int,
    reverse: bool = False,
) -> list[dict[str, str]]:
    if not rows:
        return []

    return sorted(rows, key=lambda row: _sort_value(row.get(sort_column, "")), reverse=reverse)[:limit]


def _sort_value(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("inf")


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _escape_cell(value: str) -> str:
    return str(value).replace("|", "\\|")
