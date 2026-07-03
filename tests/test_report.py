from pathlib import Path

from typer.testing import CliRunner

from osteo_target_gwas.biology.bone_cell_context import score_bone_cell_context
from osteo_target_gwas.biology.pathway import annotate_pathway_context
from osteo_target_gwas.cli import app
from osteo_target_gwas.finemap.run_susie_placeholder import run_finemap_placeholder
from osteo_target_gwas.genes.variant_to_gene import map_variants_to_genes
from osteo_target_gwas.loci.define_loci import define_significant_loci
from osteo_target_gwas.mr.mediation import run_mediation_mr_parser
from osteo_target_gwas.mr.phe_mr import run_phe_mr_parser
from osteo_target_gwas.mr.target_mr import run_target_mr_parser
from osteo_target_gwas.qc.filter_sumstats import run_gwas_qc
from osteo_target_gwas.qtl.coloc import run_coloc_parser
from osteo_target_gwas.report.make_report import make_markdown_report
from osteo_target_gwas.targets.druggability import run_druggability_annotation
from osteo_target_gwas.targets.score import score_targets


EXAMPLE_GWAS = Path("data/example/example_gwas.tsv")
EXAMPLE_CREDIBLE_SETS = Path("data/example/credible_sets.tsv")
EXAMPLE_GENES = Path("data/example/gene_annotation.tsv")
EXAMPLE_L2G = Path("data/example/opentargets_l2g.tsv")
EXAMPLE_COLOC = Path("data/example/coloc_results.tsv")
EXAMPLE_MARKERS = Path("data/example/bone_cell_markers.tsv")
EXAMPLE_GENE_SETS = Path("data/example/pathway_gene_sets.tsv")
EXAMPLE_MR = Path("data/example/mr_results.tsv")
EXAMPLE_MEDIATION = Path("data/example/mediation_mr_results.tsv")
EXAMPLE_PHE_MR = Path("data/example/phe_mr_results.tsv")
EXAMPLE_DRUGGABILITY = Path("data/example/druggability.tsv")


REQUIRED_HEADINGS = [
    "## 1. Run summary",
    "## 2. GWAS QC summary",
    "## 3. Significant loci",
    "## 4. Candidate genes",
    "## 5. Fine-mapping evidence",
    "## 6. QTL colocalisation evidence",
    "## 7. Bone-cell context",
    "## 8. Pathway and mechanism interpretation",
    "## 9. MR target-validation evidence",
    "## 10. Mediation MR evidence",
    "## 11. Phe-MR and safety scan",
    "## 12. Druggability and tractability",
    "## 13. Top ranked targets",
    "## 14. Interpretation and caveats",
    "## 15. Recommended next analyses",
]


def prepare_sparse_results(tmp_path: Path) -> Path:
    qc_result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)
    loci_result = define_significant_loci(qc_result["harmonised_sumstats_path"], tmp_path)
    map_variants_to_genes(loci_result["loci_path"], EXAMPLE_GENES, tmp_path, EXAMPLE_L2G)
    score_targets(tmp_path)
    return tmp_path


def prepare_complete_results(tmp_path: Path) -> Path:
    qc_result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)
    loci_result = define_significant_loci(qc_result["harmonised_sumstats_path"], tmp_path)
    run_finemap_placeholder(
        gwas_path=qc_result["harmonised_sumstats_path"],
        loci_path=loci_result["loci_path"],
        credible_sets_path=EXAMPLE_CREDIBLE_SETS,
        outdir=tmp_path,
    )
    gene_result = map_variants_to_genes(loci_result["loci_path"], EXAMPLE_GENES, tmp_path, EXAMPLE_L2G)
    run_coloc_parser(EXAMPLE_COLOC, tmp_path)
    score_bone_cell_context(gene_result["locus_gene_map_path"], EXAMPLE_MARKERS, tmp_path)
    annotate_pathway_context(gene_result["locus_gene_map_path"], EXAMPLE_GENE_SETS, tmp_path)
    run_target_mr_parser(EXAMPLE_MR, tmp_path)
    run_mediation_mr_parser(EXAMPLE_MEDIATION, tmp_path)
    run_phe_mr_parser(EXAMPLE_PHE_MR, tmp_path)
    run_druggability_annotation(EXAMPLE_DRUGGABILITY, tmp_path)
    return tmp_path


def test_report_is_created(tmp_path: Path) -> None:
    results_dir = prepare_complete_results(tmp_path / "results")
    score_targets(results_dir)
    out_path = tmp_path / "reports" / "example" / "target_prioritisation_report.md"
    result = make_markdown_report(results_dir, out_path)

    assert Path(result["report_path"]).exists()


def test_required_headings_exist(tmp_path: Path) -> None:
    results_dir = prepare_complete_results(tmp_path / "results")
    score_targets(results_dir)
    out_path = tmp_path / "report.md"
    make_markdown_report(results_dir, out_path)
    report = out_path.read_text(encoding="utf-8")

    for heading in REQUIRED_HEADINGS:
        assert heading in report


def test_top_targets_table_appears(tmp_path: Path) -> None:
    results_dir = prepare_complete_results(tmp_path / "results")
    score_targets(results_dir)
    out_path = tmp_path / "report.md"
    make_markdown_report(results_dir, out_path)
    report = out_path.read_text(encoding="utf-8")

    assert "| rank | gene_name | locus_id | target_score | evidence_summary |" in report


def test_report_handles_missing_optional_files_gracefully(tmp_path: Path) -> None:
    results_dir = prepare_sparse_results(tmp_path / "results")
    out_path = tmp_path / "report.md"
    make_markdown_report(results_dir, out_path)
    report = out_path.read_text(encoding="utf-8")

    assert "not available yet" in report.lower()
    assert "## 13. Top ranked targets" in report


def test_report_cli_writes_output(tmp_path: Path) -> None:
    results_dir = prepare_complete_results(tmp_path / "results")
    score_targets(results_dir)
    out_path = tmp_path / "reports" / "example" / "target_prioritisation_report.md"

    result = CliRunner().invoke(
        app,
        [
            "report",
            "--results",
            str(results_dir),
            "--out",
            str(out_path),
        ],
    )

    assert result.exit_code == 0
    assert '"n_ranked_targets":' in result.output
    assert out_path.exists()
