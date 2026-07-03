import csv
from pathlib import Path

import pytest
from typer.testing import CliRunner

from osteo_target_gwas.cli import app
from osteo_target_gwas.mr.mediation import (
    read_mediation_mr_results,
    run_mediation_mr_parser,
)


EXAMPLE_MEDIATION = Path("data/example/mediation_mr_results.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_mediation_parser_works() -> None:
    rows = read_mediation_mr_results(EXAMPLE_MEDIATION)

    assert rows
    assert "mediation_score" in rows[0]


def test_invalid_proportion_fails(tmp_path: Path) -> None:
    rows = read_tsv(EXAMPLE_MEDIATION)
    rows[0]["proportion_mediated"] = "1.3"
    invalid_path = tmp_path / "invalid_mediation.tsv"
    write_tsv(invalid_path, rows)

    with pytest.raises(ValueError, match="Invalid proportion_mediated"):
        read_mediation_mr_results(invalid_path)


def test_mediation_summary_created(tmp_path: Path) -> None:
    result = run_mediation_mr_parser(EXAMPLE_MEDIATION, tmp_path)
    summary_path = Path(result["gene_mediation_summary_path"])
    summary_rows = read_tsv(summary_path)

    assert summary_path.exists()
    assert summary_rows
    assert "mediation_score" in summary_rows[0]


def test_mediation_score_between_zero_and_one() -> None:
    rows = read_mediation_mr_results(EXAMPLE_MEDIATION)

    assert all(0 <= float(row["mediation_score"]) <= 1 for row in rows)


def test_mediation_mr_cli_writes_outputs(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "mediation-mr",
            "--mediation",
            str(EXAMPLE_MEDIATION),
            "--outdir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert '"n_mediation_records":' in result.output
    assert (tmp_path / "mr" / "mediation_mr_results.tsv").exists()
    assert (tmp_path / "mr" / "gene_mediation_summary.tsv").exists()
