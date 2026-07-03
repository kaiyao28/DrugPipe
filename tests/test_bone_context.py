import csv
from pathlib import Path

from typer.testing import CliRunner

from osteo_target_gwas.biology.bone_cell_context import (
    BONE_CELL_CONTEXT_COLUMNS,
    CELL_TYPES,
    score_bone_cell_context,
)
from osteo_target_gwas.cli import app
from osteo_target_gwas.genes.variant_to_gene import map_variants_to_genes
from osteo_target_gwas.loci.define_loci import define_significant_loci
from osteo_target_gwas.qc.filter_sumstats import run_gwas_qc


EXAMPLE_GWAS = Path("data/example/example_gwas.tsv")
EXAMPLE_GENES = Path("data/example/gene_annotation.tsv")
EXAMPLE_L2G = Path("data/example/l2g_scores.tsv")
EXAMPLE_MARKERS = Path("data/example/bone_cell_markers.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def prepare_gene_map(tmp_path: Path) -> str:
    qc_result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)
    loci_result = define_significant_loci(qc_result["harmonised_sumstats_path"], tmp_path)
    gene_result = map_variants_to_genes(loci_result["loci_path"], EXAMPLE_GENES, tmp_path, EXAMPLE_L2G)
    return gene_result["locus_gene_map_path"]


def test_bone_context_output_created(tmp_path: Path) -> None:
    gene_map_path = prepare_gene_map(tmp_path)
    result = score_bone_cell_context(gene_map_path, EXAMPLE_MARKERS, tmp_path)

    assert Path(result["bone_cell_relevance_path"]).exists()
    assert read_tsv(Path(result["bone_cell_relevance_path"]))


def test_all_cell_type_score_columns_exist(tmp_path: Path) -> None:
    gene_map_path = prepare_gene_map(tmp_path)
    result = score_bone_cell_context(gene_map_path, EXAMPLE_MARKERS, tmp_path)
    rows = read_tsv(Path(result["bone_cell_relevance_path"]))

    assert rows
    assert list(rows[0]) == BONE_CELL_CONTEXT_COLUMNS
    for cell_type in CELL_TYPES:
        assert f"{cell_type}_score" in rows[0]


def test_bone_cell_context_score_between_zero_and_one(tmp_path: Path) -> None:
    gene_map_path = prepare_gene_map(tmp_path)
    result = score_bone_cell_context(gene_map_path, EXAMPLE_MARKERS, tmp_path)
    rows = read_tsv(Path(result["bone_cell_relevance_path"]))

    assert all(0 <= float(row["bone_cell_context_score"]) <= 1 for row in rows)


def test_unknown_assigned_for_missing_markers(tmp_path: Path) -> None:
    gene_map = tmp_path / "gene_map.tsv"
    gene_map.write_text(
        "locus_id\tgene_id\tgene_name\tCHR\tgene_start\tgene_end\ttss\tnearest_gene\t"
        "distance_to_tss\tlocus_overlap\tl2g_score\tlocus_to_gene_score\tevidence_labels\n"
        "locus1\tENSG_SYN_NONE\tNO_MARKER\t1\t100\t200\t100\ttrue\t0\ttrue\t0\t0.7\tnearest_gene;locus_overlap\n",
        encoding="utf-8",
    )

    result = score_bone_cell_context(gene_map, EXAMPLE_MARKERS, tmp_path)
    rows = read_tsv(Path(result["bone_cell_relevance_path"]))

    assert rows[0]["gene_name"] == "NO_MARKER"
    assert rows[0]["top_cell_context"] == "unknown"
    assert rows[0]["bone_cell_context_score"] == "0"


def test_bone_context_cli_writes_output(tmp_path: Path) -> None:
    gene_map_path = prepare_gene_map(tmp_path)
    result = CliRunner().invoke(
        app,
        [
            "bone-context",
            "--gene-map",
            gene_map_path,
            "--markers",
            str(EXAMPLE_MARKERS),
            "--outdir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert '"n_genes":' in result.output
    assert (tmp_path / "cell_context" / "bone_cell_relevance.tsv").exists()
