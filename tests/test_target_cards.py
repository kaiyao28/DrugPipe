import csv
from pathlib import Path

from typer.testing import CliRunner

from osteo_target_gwas.cli import app
from osteo_target_gwas.report.target_cards import make_target_cards


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def prepare_card_results(tmp_path: Path) -> Path:
    write_tsv(
        tmp_path / "targets" / "ranked_targets.tsv",
        [
            {
                "rank": "1",
                "gene_name": "SOST",
                "locus_id": "locus1",
                "target_score": "0.82",
                "genetic_association_score": "0.22",
                "fine_mapping_score": "0.66",
                "locus_to_gene_score": "0.98",
                "qtl_colocalisation_score": "0.82",
                "bone_cell_context_score": "0.96",
                "pathway_context_score": "0.67",
                "mr_target_validation_score": "0.26",
                "mediation_score": "0.03",
                "druggability_score": "1",
                "phe_mr_safety_penalty": "0",
                "annotation_bias_penalty": "0",
                "top_cell_context": "osteocyte",
                "best_qtl_type": "eQTL",
                "best_effect_direction": "increased_expression_increases_risk",
                "best_mr_outcome": "fracture_risk",
                "best_mediator": "BMI",
                "target_class": "secreted_protein",
                "known_drug": "true",
                "known_drug_name": "synthetic_reference",
                "evidence_summary": "genetic association; druggability",
            },
            {
                "rank": "2",
                "gene_name": "LRP5",
                "locus_id": "locus2",
                "target_score": "0.55",
                "genetic_association_score": "0.21",
                "fine_mapping_score": "0.58",
                "locus_to_gene_score": "0.97",
                "qtl_colocalisation_score": "0.74",
                "bone_cell_context_score": "0.76",
                "pathway_context_score": "0.33",
                "mr_target_validation_score": "0.27",
                "mediation_score": "0.02",
                "druggability_score": "0.61",
                "phe_mr_safety_penalty": "0.1",
                "annotation_bias_penalty": "0",
                "top_cell_context": "mesenchymal_stromal_cell",
                "best_qtl_type": "eQTL",
                "best_effect_direction": "increased_expression_increases_BMD",
                "best_mr_outcome": "heel_BMD",
                "best_mediator": "insulin_resistance",
                "target_class": "receptor",
                "known_drug": "false",
                "known_drug_name": "NA",
                "evidence_summary": "genetic association",
            },
        ],
    )
    write_tsv(tmp_path / "loci" / "loci.tsv", [{"locus_id": "locus1", "LEAD_SNP": "rsSOST001"}])
    write_tsv(
        tmp_path / "genes" / "locus_gene_map.tsv",
        [{"gene_name": "SOST", "locus_id": "locus1", "evidence_labels": "nearest_gene;l2g", "distance_to_tss": "5000"}],
    )
    write_tsv(
        tmp_path / "qtl" / "gene_coloc_summary.tsv",
        [{"gene_name": "SOST", "max_pp_h4": "0.82", "best_qtl_type": "eQTL", "best_tissue_or_cell": "osteocyte", "best_effect_direction": "increased_expression_increases_risk"}],
    )
    write_tsv(
        tmp_path / "cell_context" / "bone_cell_relevance.tsv",
        [{"gene_name": "SOST", "osteoblast_score": "0", "osteoclast_score": "0", "osteocyte_score": "0.96", "top_cell_context": "osteocyte"}],
    )
    write_tsv(tmp_path / "biology" / "gene_pathway_context.tsv", [{"gene_name": "SOST", "pathways": "WNT_signalling;bone_mineralisation"}])
    write_tsv(
        tmp_path / "mr" / "gene_mr_summary.tsv",
        [{"gene_name": "SOST", "best_beta": "0.084", "best_p": "0.0027", "best_f_statistic": "44.6", "best_outcome": "fracture_risk", "mr_direction": "higher_exposure_higher_fracture_risk"}],
    )
    write_tsv(
        tmp_path / "mr" / "gene_mediation_summary.tsv",
        [{"gene_name": "SOST", "best_mediator": "BMI", "best_mediator_category": "anthropometric", "best_proportion_mediated": "0.19"}],
    )
    write_tsv(
        tmp_path / "mr" / "gene_phe_mr_safety_summary.tsv",
        [{"gene_name": "SOST", "n_liability_flags": "0", "strongest_liability_trait": "none", "phe_mr_safety_penalty": "0"}],
    )
    write_tsv(
        tmp_path / "targets" / "druggability.tsv",
        [{"gene_name": "SOST", "target_class": "secreted_protein", "tractability_modality": "antibody", "known_drug": "true", "known_drug_name": "synthetic_reference", "druggability_score": "1"}],
    )
    return tmp_path


def test_cards_are_created(tmp_path: Path) -> None:
    results_dir = prepare_card_results(tmp_path / "results")
    outdir = tmp_path / "cards"
    result = make_target_cards(results_dir, outdir, top_n=2)

    assert result["n_cards"] == 2
    assert all(Path(path).exists() for path in result["target_card_paths"])


def test_card_filenames_use_gene_names(tmp_path: Path) -> None:
    results_dir = prepare_card_results(tmp_path / "results")
    outdir = tmp_path / "cards"
    make_target_cards(results_dir, outdir, top_n=1)

    assert (outdir / "SOST.md").exists()


def test_required_sections_exist(tmp_path: Path) -> None:
    results_dir = prepare_card_results(tmp_path / "results")
    outdir = tmp_path / "cards"
    make_target_cards(results_dir, outdir, top_n=1)
    card = (outdir / "SOST.md").read_text(encoding="utf-8")

    for heading in [
        "# Target: SOST",
        "## Overall priority",
        "## Genetic evidence",
        "## Locus-to-gene evidence",
        "## Molecular QTL evidence",
        "## Bone-cell context",
        "## Mechanism and pathway context",
        "## MR target-validation evidence",
        "## Mediation evidence",
        "## Phe-MR and safety",
        "## Druggability",
        "## Interpretation",
    ]:
        assert heading in card


def test_top_n_respected(tmp_path: Path) -> None:
    results_dir = prepare_card_results(tmp_path / "results")
    outdir = tmp_path / "cards"
    result = make_target_cards(results_dir, outdir, top_n=1)

    assert result["n_cards"] == 1
    assert (outdir / "SOST.md").exists()
    assert not (outdir / "LRP5.md").exists()


def test_make_target_cards_cli_writes_cards(tmp_path: Path) -> None:
    results_dir = prepare_card_results(tmp_path / "results")
    outdir = tmp_path / "cards"
    result = CliRunner().invoke(
        app,
        [
            "make-target-cards",
            "--results",
            str(results_dir),
            "--top-n",
            "1",
            "--outdir",
            str(outdir),
        ],
    )

    assert result.exit_code == 0
    assert '"n_cards": 1' in result.output
    assert (outdir / "SOST.md").exists()
