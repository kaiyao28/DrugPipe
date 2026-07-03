import csv
from pathlib import Path

from typer.testing import CliRunner

from osteo_target_gwas.cli import app
from osteo_target_gwas.genes.variant_to_gene import LOCUS_GENE_COLUMNS, map_variants_to_genes
from osteo_target_gwas.loci.define_loci import define_significant_loci
from osteo_target_gwas.qc.filter_sumstats import run_gwas_qc


EXAMPLE_GWAS = Path("data/example/example_gwas.tsv")
EXAMPLE_GENES = Path("data/example/gene_annotation.tsv")
EXAMPLE_L2G = Path("data/example/opentargets_l2g.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def prepare_loci(tmp_path: Path) -> str:
    qc_result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)
    loci_result = define_significant_loci(qc_result["harmonised_sumstats_path"], tmp_path)
    return loci_result["loci_path"]


def test_maps_at_least_one_gene_per_locus(tmp_path: Path) -> None:
    loci_path = prepare_loci(tmp_path)
    result = map_variants_to_genes(loci_path, EXAMPLE_GENES, tmp_path, EXAMPLE_L2G)
    rows = read_tsv(Path(result["locus_gene_map_path"]))
    loci = read_tsv(Path(loci_path))

    mapped_loci = {row["locus_id"] for row in rows}

    assert rows
    assert {locus["locus_id"] for locus in loci} <= mapped_loci


def test_nearest_gene_is_identified(tmp_path: Path) -> None:
    loci_path = prepare_loci(tmp_path)
    result = map_variants_to_genes(loci_path, EXAMPLE_GENES, tmp_path, EXAMPLE_L2G)
    rows = read_tsv(Path(result["locus_gene_map_path"]))

    nearest_rows = [row for row in rows if row["nearest_gene"] == "true"]

    assert nearest_rows
    assert all(row["distance_to_tss"].isdigit() for row in nearest_rows)


def test_locus_to_gene_score_is_between_zero_and_one(tmp_path: Path) -> None:
    loci_path = prepare_loci(tmp_path)
    result = map_variants_to_genes(loci_path, EXAMPLE_GENES, tmp_path, EXAMPLE_L2G)
    rows = read_tsv(Path(result["locus_gene_map_path"]))

    assert rows
    assert all(0 <= float(row["locus_to_gene_score"]) <= 1 for row in rows)


def test_evidence_labels_are_created(tmp_path: Path) -> None:
    loci_path = prepare_loci(tmp_path)
    result = map_variants_to_genes(loci_path, EXAMPLE_GENES, tmp_path, EXAMPLE_L2G)
    rows = read_tsv(Path(result["locus_gene_map_path"]))
    labels = {label for row in rows for label in row["evidence_labels"].split(";") if label}

    assert {"nearest_gene", "locus_overlap", "l2g"} <= labels


def test_locus_gene_output_columns_exist(tmp_path: Path) -> None:
    loci_path = prepare_loci(tmp_path)
    result = map_variants_to_genes(loci_path, EXAMPLE_GENES, tmp_path, EXAMPLE_L2G)
    rows = read_tsv(Path(result["locus_gene_map_path"]))

    assert rows
    assert list(rows[0]) == LOCUS_GENE_COLUMNS


def test_map_genes_cli_writes_output(tmp_path: Path) -> None:
    loci_path = prepare_loci(tmp_path)
    result = CliRunner().invoke(
        app,
        [
            "map-genes",
            "--loci",
            loci_path,
            "--genes",
            str(EXAMPLE_GENES),
            "--l2g",
            str(EXAMPLE_L2G),
            "--outdir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert '"n_gene_links":' in result.output
    assert (tmp_path / "genes" / "locus_gene_map.tsv").exists()
