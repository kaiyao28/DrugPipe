"""Markdown reporting for GWAS summary-statistic QC."""

from __future__ import annotations

from typing import Any


def render_qc_report(summary: dict[str, Any]) -> str:
    """Render a compact Markdown QC report from a summary dictionary."""

    lines = [
        "# GWAS QC Report",
        "",
        "## Summary",
        "",
        f"- Input variants: {summary['n_input_variants']}",
        f"- Output variants: {summary['n_output_variants']}",
        f"- Removed for low INFO: {summary['n_removed_low_info']}",
        f"- Removed for low MAF: {summary['n_removed_low_maf']}",
        f"- Removed for missing BETA/SE/P: {summary['n_removed_missing']}",
        f"- Removed ambiguous A/T or C/G SNPs: {summary['n_removed_ambiguous']}",
        f"- Minimum P-value after QC: {summary['min_p']}",
        f"- Genome-wide significant variants after QC: {summary['n_genome_wide_significant']}",
        "",
    ]
    return "\n".join(lines)
