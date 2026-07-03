import csv
import gzip
import json
from pathlib import Path

from typer.testing import CliRunner

from osteo_target_gwas.cli import app
from osteo_target_gwas.qc.filter_sumstats import run_gwas_qc


EXAMPLE_GWAS = Path("data/example/example_gwas.tsv")
SUMMARY_KEYS = {
    "n_input_variants",
    "n_output_variants",
    "n_removed_low_info",
    "n_removed_low_maf",
    "n_removed_missing",
    "n_removed_ambiguous",
    "min_p",
    "n_genome_wide_significant",
}


def read_harmonised(path: Path) -> list[dict[str, str]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_qc_creates_expected_files(tmp_path: Path) -> None:
    result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)

    assert Path(result["harmonised_sumstats_path"]).exists()
    assert Path(result["qc_summary_path"]).exists()
    assert Path(result["qc_report_path"]).exists()


def test_maf_column_is_created(tmp_path: Path) -> None:
    result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)
    rows = read_harmonised(Path(result["harmonised_sumstats_path"]))

    assert rows
    assert "MAF" in rows[0]
    assert float(rows[0]["MAF"]) == min(float(rows[0]["EAF"]), 1 - float(rows[0]["EAF"]))


def test_ambiguous_snps_are_removed_when_requested(tmp_path: Path) -> None:
    result = run_gwas_qc(EXAMPLE_GWAS, tmp_path, remove_ambiguous=True)
    rows = read_harmonised(Path(result["harmonised_sumstats_path"]))
    allele_pairs = {(row["A1"], row["A2"]) for row in rows}

    assert result["summary"]["n_removed_ambiguous"] > 0
    assert ("A", "T") not in allele_pairs
    assert ("T", "A") not in allele_pairs
    assert ("C", "G") not in allele_pairs
    assert ("G", "C") not in allele_pairs


def test_qc_summary_has_expected_keys(tmp_path: Path) -> None:
    result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)
    summary_path = Path(result["qc_summary_path"])
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert SUMMARY_KEYS <= set(summary)


def test_qc_cli_creates_expected_files(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "qc",
            "--gwas",
            str(EXAMPLE_GWAS),
            "--outdir",
            str(tmp_path),
            "--min-info",
            "0.8",
            "--min-maf",
            "0.01",
            "--remove-ambiguous",
        ],
    )

    assert result.exit_code == 0
    assert '"n_input_variants":' in result.output
    assert (tmp_path / "qc" / "harmonised_sumstats.tsv.gz").exists()
    assert (tmp_path / "qc" / "qc_summary.json").exists()
    assert (tmp_path / "qc" / "qc_report.md").exists()
