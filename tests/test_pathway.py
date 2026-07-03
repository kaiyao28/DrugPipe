import csv
from pathlib import Path

from typer.testing import CliRunner

from osteo_target_gwas.biology.pathway import annotate_pathway_context
from osteo_target_gwas.cli import app
from osteo_target_gwas.genes.variant_to_gene import map_variants_to_genes
from osteo_target_gwas.loci.define_loci import define_significant_loci
from osteo_target_gwas.qc.filter_sumstats import run_gwas_qc


EXAMPLE_GWAS = Path("data/example/example_gwas.tsv")
EXAMPLE_GENES = Path("data/example/gene_annotation.tsv")
EXAMPLE_L2G = Path("data/example/l2g_scores.tsv")
EXAMPLE_GENE_SETS = Path("data/example/pathway_gene_sets.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def prepare_gene_map(tmp_path: Path) -> str:
    qc_result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)
    loci_result = define_significant_loci(qc_result["harmonised_sumstats_path"], tmp_path)
    gene_result = map_variants_to_genes(loci_result["loci_path"], EXAMPLE_GENES, tmp_path, EXAMPLE_L2G)
    return gene_result["locus_gene_map_path"]


def test_gene_pathway_context_created(tmp_path: Path) -> None:
    gene_map_path = prepare_gene_map(tmp_path)
    result = annotate_pathway_context(gene_map_path, EXAMPLE_GENE_SETS, tmp_path)

    assert Path(result["gene_pathway_context_path"]).exists()
    assert read_tsv(Path(result["gene_pathway_context_path"]))


def test_pathway_summary_created(tmp_path: Path) -> None:
    gene_map_path = prepare_gene_map(tmp_path)
    result = annotate_pathway_context(gene_map_path, EXAMPLE_GENE_SETS, tmp_path)

    assert Path(result["pathway_summary_path"]).exists()
    assert read_tsv(Path(result["pathway_summary_path"]))


def test_wnt_signalling_present_if_matching_genes_exist(tmp_path: Path) -> None:
    gene_map_path = prepare_gene_map(tmp_path)
    result = annotate_pathway_context(gene_map_path, EXAMPLE_GENE_SETS, tmp_path)
    summary_rows = read_tsv(Path(result["pathway_summary_path"]))
    pathway_names = {row["pathway_name"] for row in summary_rows}

    assert "WNT_signalling" in pathway_names


def test_pathway_scores_between_zero_and_one(tmp_path: Path) -> None:
    gene_map_path = prepare_gene_map(tmp_path)
    result = annotate_pathway_context(gene_map_path, EXAMPLE_GENE_SETS, tmp_path)
    rows = read_tsv(Path(result["gene_pathway_context_path"]))

    assert rows
    assert all(0 <= float(row["pathway_context_score"]) <= 1 for row in rows)


def test_pathway_cli_writes_outputs(tmp_path: Path) -> None:
    gene_map_path = prepare_gene_map(tmp_path)
    result = CliRunner().invoke(
        app,
        [
            "pathway",
            "--gene-map",
            gene_map_path,
            "--gene-sets",
            str(EXAMPLE_GENE_SETS),
            "--outdir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert '"n_pathways":' in result.output
    assert (tmp_path / "biology" / "gene_pathway_context.tsv").exists()
    assert (tmp_path / "biology" / "pathway_summary.tsv").exists()
