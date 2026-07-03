import csv
from pathlib import Path

from typer.testing import CliRunner

from osteo_target_gwas.cli import app
from osteo_target_gwas.mr.phe_mr import read_phe_mr_results, run_phe_mr_parser


EXAMPLE_PHE_MR = Path("data/example/phe_mr_results.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_phe_mr_parser_works() -> None:
    rows = read_phe_mr_results(EXAMPLE_PHE_MR)

    assert rows
    assert "possible_liability" in rows[0]
    assert "safety_penalty" in rows[0]


def test_liability_flags_are_detected() -> None:
    rows = read_phe_mr_results(EXAMPLE_PHE_MR)

    assert any(row["possible_liability"] == "true" for row in rows)


def test_penalty_is_assigned() -> None:
    rows = read_phe_mr_results(EXAMPLE_PHE_MR)
    monitor_rows = [row for row in rows if row["safety_flag"] == "monitor"]

    assert monitor_rows
    assert all(row["safety_penalty"] == "0.1" for row in monitor_rows)


def test_phe_mr_summary_created(tmp_path: Path) -> None:
    result = run_phe_mr_parser(EXAMPLE_PHE_MR, tmp_path)
    summary_path = Path(result["gene_phe_mr_safety_summary_path"])
    summary_rows = read_tsv(summary_path)

    assert summary_path.exists()
    assert summary_rows
    assert "phe_mr_safety_penalty" in summary_rows[0]


def test_phe_mr_cli_writes_outputs(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "phe-mr",
            "--phe-mr",
            str(EXAMPLE_PHE_MR),
            "--outdir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert '"n_phe_mr_records":' in result.output
    assert (tmp_path / "mr" / "phe_mr_results.tsv").exists()
    assert (tmp_path / "mr" / "gene_phe_mr_safety_summary.tsv").exists()
