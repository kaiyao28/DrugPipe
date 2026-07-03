import csv
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
from osteo_target_gwas.targets.druggability import run_druggability_annotation
from osteo_target_gwas.targets.score import score_targets


EXAMPLE_GWAS = Path("data/example/example_gwas.tsv")
EXAMPLE_CREDIBLE_SETS = Path("data/example/credible_sets.tsv")
EXAMPLE_GENES = Path("data/example/gene_annotation.tsv")
EXAMPLE_L2G = Path("data/example/l2g_scores.tsv")
EXAMPLE_COLOC = Path("data/example/coloc_results.tsv")
EXAMPLE_MARKERS = Path("data/example/bone_cell_markers.tsv")
EXAMPLE_GENE_SETS = Path("data/example/pathway_gene_sets.tsv")
EXAMPLE_MR = Path("data/example/mr_results.tsv")
EXAMPLE_MEDIATION = Path("data/example/mediation_mr_results.tsv")
EXAMPLE_PHE_MR = Path("data/example/phe_mr_results.tsv")
EXAMPLE_DRUGGABILITY = Path("data/example/druggability.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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


def test_ranked_targets_file_created(tmp_path: Path) -> None:
    results_dir = prepare_complete_results(tmp_path)
    result = score_targets(results_dir)

    assert Path(result["ranked_targets_path"]).exists()
    assert read_tsv(Path(result["ranked_targets_path"]))


def test_target_score_numeric(tmp_path: Path) -> None:
    results_dir = prepare_complete_results(tmp_path)
    result = score_targets(results_dir)
    rows = read_tsv(Path(result["ranked_targets_path"]))

    assert all(isinstance(float(row["target_score"]), float) for row in rows)


def test_ranks_are_sorted_descending(tmp_path: Path) -> None:
    results_dir = prepare_complete_results(tmp_path)
    result = score_targets(results_dir)
    rows = read_tsv(Path(result["ranked_targets_path"]))
    scores = [float(row["target_score"]) for row in rows]

    assert [int(row["rank"]) for row in rows] == list(range(1, len(rows) + 1))
    assert scores == sorted(scores, reverse=True)


def test_missing_evidence_does_not_crash(tmp_path: Path) -> None:
    qc_result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)
    loci_result = define_significant_loci(qc_result["harmonised_sumstats_path"], tmp_path)
    map_variants_to_genes(loci_result["loci_path"], EXAMPLE_GENES, tmp_path, EXAMPLE_L2G)

    result = score_targets(tmp_path)
    rows = read_tsv(Path(result["ranked_targets_path"]))

    assert rows
    assert all(float(row["fine_mapping_score"]) == 0 for row in rows)


def test_known_example_genes_are_present(tmp_path: Path) -> None:
    results_dir = prepare_complete_results(tmp_path)
    result = score_targets(results_dir)
    rows = read_tsv(Path(result["ranked_targets_path"]))
    genes = {row["gene_name"] for row in rows}

    assert {"SOST", "LRP5", "WNT16"} <= genes


def test_score_targets_cli_writes_output(tmp_path: Path) -> None:
    results_dir = prepare_complete_results(tmp_path)
    result = CliRunner().invoke(
        app,
        [
            "score-targets",
            "--results",
            str(results_dir),
            "--config",
            "config/default.yaml",
        ],
    )

    assert result.exit_code == 0
    assert '"n_targets":' in result.output
    assert (results_dir / "targets" / "ranked_targets.tsv").exists()
