import csv
from pathlib import Path

import pytest
from typer.testing import CliRunner

from osteo_target_gwas.cli import app
from osteo_target_gwas.qtl.coloc import (
    read_coloc_results,
    run_coloc_parser,
    summarise_coloc_by_gene,
)


EXAMPLE_COLOC = Path("data/example/coloc_results.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_valid_coloc_file_parses() -> None:
    rows = read_coloc_results(EXAMPLE_COLOC)

    assert rows
    assert rows[0]["gene_name"]


def test_invalid_posterior_fails(tmp_path: Path) -> None:
    rows = read_tsv(EXAMPLE_COLOC)
    rows[0]["pp_h4"] = "1.2"
    invalid_path = tmp_path / "invalid_coloc.tsv"
    write_tsv(invalid_path, rows)

    with pytest.raises(ValueError, match="Invalid pp_h4"):
        read_coloc_results(invalid_path)


def test_gene_summary_created(tmp_path: Path) -> None:
    result = run_coloc_parser(EXAMPLE_COLOC, tmp_path)
    summary_path = Path(result["gene_coloc_summary_path"])
    summary_rows = read_tsv(summary_path)

    assert summary_path.exists()
    assert summary_rows
    assert "qtl_colocalisation_score" in summary_rows[0]


def test_coloc_score_between_zero_and_one() -> None:
    rows = read_coloc_results(EXAMPLE_COLOC)
    summary_rows = summarise_coloc_by_gene(rows)

    assert summary_rows
    assert all(0 <= float(row["qtl_colocalisation_score"]) <= 1 for row in summary_rows)


def test_coloc_cli_writes_outputs(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "coloc",
            "--coloc",
            str(EXAMPLE_COLOC),
            "--outdir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert '"n_coloc_records":' in result.output
    assert (tmp_path / "qtl" / "coloc_results.tsv").exists()
    assert (tmp_path / "qtl" / "gene_coloc_summary.tsv").exists()
