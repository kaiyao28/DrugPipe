import csv
from pathlib import Path

from typer.testing import CliRunner

from osteo_target_gwas.cli import app
from osteo_target_gwas.mr.target_mr import read_mr_results, run_target_mr_parser


EXAMPLE_MR = Path("data/example/mr_results.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_mr_results_parse() -> None:
    rows = read_mr_results(EXAMPLE_MR)

    assert rows
    assert "mr_evidence_score" in rows[0]
    assert "strong_instrument" in rows[0]


def test_weak_instruments_receive_score_zero(tmp_path: Path) -> None:
    rows = read_tsv(EXAMPLE_MR)
    rows[0]["f_statistic"] = "9.9"
    weak_path = tmp_path / "weak_mr.tsv"
    write_tsv(weak_path, rows)

    parsed = read_mr_results(weak_path)

    assert parsed[0]["strong_instrument"] == "false"
    assert parsed[0]["mr_evidence_score"] == "0"


def test_mr_summary_created(tmp_path: Path) -> None:
    result = run_target_mr_parser(EXAMPLE_MR, tmp_path)
    summary_path = Path(result["gene_mr_summary_path"])
    summary_rows = read_tsv(summary_path)

    assert summary_path.exists()
    assert summary_rows
    assert "mr_target_validation_score" in summary_rows[0]


def test_mr_score_between_zero_and_one() -> None:
    rows = read_mr_results(EXAMPLE_MR)

    assert all(0 <= float(row["mr_evidence_score"]) <= 1 for row in rows)


def test_mr_targets_cli_writes_outputs(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "mr-targets",
            "--mr",
            str(EXAMPLE_MR),
            "--outdir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert '"n_mr_records":' in result.output
    assert (tmp_path / "mr" / "target_mr_results.tsv").exists()
    assert (tmp_path / "mr" / "gene_mr_summary.tsv").exists()
