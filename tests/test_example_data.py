import csv
from pathlib import Path


EXAMPLE_DIR = Path("data/example")

REQUIRED_COLUMNS = {
    "example_gwas.tsv": ["SNP", "CHR", "BP", "A1", "A2", "BETA", "SE", "P", "EAF", "N", "INFO"],
    "gene_annotation.tsv": ["gene_id", "gene_name", "chr", "start", "end", "tss", "strand", "gene_type"],
    "opentargets_evidence.tsv": [
        "gene_id",
        "gene_name",
        "disease_name",
        "genetic_association_score",
        "tractability_score",
        "known_drug_score",
        "safety_score",
        "datasource",
    ],
    "bone_cell_markers.tsv": ["gene_name", "cell_type", "marker_strength"],
    "pathway_gene_sets.tsv": ["pathway_name", "gene_name"],
    "coloc_results.tsv": ["locus_id", "gene_name", "qtl_type", "tissue_or_cell", "pp_h4", "pp_h3", "effect_direction"],
    "mr_results.tsv": ["gene_name", "exposure_type", "exposure_id", "outcome", "beta", "se", "p", "f_statistic", "method", "direction"],
    "mediation_mr_results.tsv": ["gene_name", "mediator", "mediator_category", "indirect_effect", "se", "p", "proportion_mediated"],
    "phe_mr_results.tsv": ["gene_name", "outcome_trait", "beta", "se", "p", "category", "safety_flag"],
    "druggability.tsv": ["gene_name", "target_class", "tractability_modality", "tractability_score", "known_drug", "known_drug_name", "safety_note"],
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_all_example_files_exist() -> None:
    for filename in REQUIRED_COLUMNS:
        assert (EXAMPLE_DIR / filename).exists()


def test_example_files_are_not_empty() -> None:
    for filename in REQUIRED_COLUMNS:
        rows = read_tsv(EXAMPLE_DIR / filename)

        assert rows


def test_example_files_have_required_columns() -> None:
    for filename, columns in REQUIRED_COLUMNS.items():
        rows = read_tsv(EXAMPLE_DIR / filename)

        assert rows
        assert columns == list(rows[0])


def test_example_gwas_has_sixty_variants_and_four_significant_loci() -> None:
    rows = read_tsv(EXAMPLE_DIR / "example_gwas.tsv")
    significant_loci = {
        row["SNP"].removeprefix("rs").rstrip("0123456789")
        for row in rows
        if float(row["P"]) < 5e-8
    }

    assert len(rows) >= 60
    assert len(significant_loci) >= 4
