"""Fine-mapping runner placeholder for precomputed credible-set workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from osteo_target_gwas.finemap.parse_credible_sets import (
    read_credible_sets,
    summarise_finemap_by_locus,
    write_credible_sets,
    write_locus_finemap_summary,
)


def run_finemap_placeholder(
    gwas_path: str | Path,
    loci_path: str | Path,
    outdir: str | Path,
    credible_sets_path: str | Path | None = None,
) -> dict[str, Any]:
    """Write fine-mapping-ready outputs from precomputed credible sets."""

    if credible_sets_path is None:
        msg = (
            "Real SuSiE/FINEMAP wrapping is not implemented yet; precomputed "
            "credible sets are currently expected via --credible-sets."
        )
        raise NotImplementedError(msg)

    # These inputs are required by the CLI contract and future runner, even though
    # the placeholder only copies/summarises precomputed credible-set records.
    _ensure_exists(gwas_path, "GWAS")
    _ensure_exists(loci_path, "loci")

    credible_sets = read_credible_sets(credible_sets_path)
    summary = summarise_finemap_by_locus(credible_sets)

    output_dir = Path(outdir) / "finemap"
    output_credible_sets = output_dir / "credible_sets.tsv"
    output_summary = output_dir / "locus_finemap_summary.tsv"

    write_credible_sets(output_credible_sets, credible_sets)
    write_locus_finemap_summary(output_summary, summary)

    return {
        "credible_sets_path": str(output_credible_sets),
        "locus_finemap_summary_path": str(output_summary),
        "n_credible_set_variants": len(credible_sets),
        "n_loci": len(summary),
    }


def _ensure_exists(path: str | Path, label: str) -> None:
    if not Path(path).exists():
        msg = f"Expected {label} file does not exist: {path}"
        raise FileNotFoundError(msg)
