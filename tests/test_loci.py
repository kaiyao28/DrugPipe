import csv
from pathlib import Path

from typer.testing import CliRunner

from osteo_target_gwas.cli import app
from osteo_target_gwas.loci.annotate_loci import LOCUS_OUTPUT_COLUMNS
from osteo_target_gwas.loci.define_loci import define_significant_loci
from osteo_target_gwas.qc.filter_sumstats import run_gwas_qc


EXAMPLE_GWAS = Path("data/example/example_gwas.tsv")


def read_loci(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_gwas(path: Path, rows: list[dict[str, str]]) -> None:
    columns = ["SNP", "CHR", "BP", "A1", "A2", "BETA", "SE", "P", "EAF", "N", "INFO"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_loci_are_created_from_example_data(tmp_path: Path) -> None:
    qc_result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)
    loci_result = define_significant_loci(qc_result["harmonised_sumstats_path"], tmp_path)

    loci = read_loci(Path(loci_result["loci_path"]))

    assert loci
    assert loci_result["n_loci"] == len(loci)


def test_overlapping_loci_are_merged(tmp_path: Path) -> None:
    gwas_path = tmp_path / "overlap.tsv"
    write_gwas(
        gwas_path,
        [
            {"SNP": "rs1", "CHR": "1", "BP": "1000", "A1": "A", "A2": "C", "BETA": "0.1", "SE": "0.02", "P": "1e-9", "EAF": "0.40", "N": "1000", "INFO": "0.99"},
            {"SNP": "rs2", "CHR": "1", "BP": "1500", "A1": "G", "A2": "A", "BETA": "0.2", "SE": "0.03", "P": "1e-10", "EAF": "0.35", "N": "1000", "INFO": "0.98"},
            {"SNP": "rs3", "CHR": "1", "BP": "1900", "A1": "T", "A2": "G", "BETA": "0.05", "SE": "0.02", "P": "0.03", "EAF": "0.20", "N": "1000", "INFO": "0.97"},
        ],
    )

    loci_result = define_significant_loci(gwas_path, tmp_path, p_threshold=5e-8, window_kb=1)
    loci = read_loci(Path(loci_result["loci_path"]))

    assert len(loci) == 1
    assert loci[0]["START"] == "1"
    assert loci[0]["END"] == "2500"
    assert loci[0]["N_VARIANTS"] == "3"
    assert loci[0]["N_SIGNIFICANT_VARIANTS"] == "2"


def test_lead_snp_is_lowest_p_value_snp(tmp_path: Path) -> None:
    gwas_path = tmp_path / "lead.tsv"
    write_gwas(
        gwas_path,
        [
            {"SNP": "rs_less_significant", "CHR": "2", "BP": "5000", "A1": "A", "A2": "C", "BETA": "0.1", "SE": "0.02", "P": "2e-9", "EAF": "0.40", "N": "1000", "INFO": "0.99"},
            {"SNP": "rs_lead", "CHR": "2", "BP": "5300", "A1": "G", "A2": "T", "BETA": "0.3", "SE": "0.03", "P": "4e-12", "EAF": "0.35", "N": "1000", "INFO": "0.98"},
        ],
    )

    loci_result = define_significant_loci(gwas_path, tmp_path, p_threshold=5e-8, window_kb=1)
    loci = read_loci(Path(loci_result["loci_path"]))

    assert loci[0]["LEAD_SNP"] == "rs_lead"
    assert loci[0]["LEAD_P"] == "4e-12"


def test_loci_output_columns_exist(tmp_path: Path) -> None:
    qc_result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)
    loci_result = define_significant_loci(qc_result["harmonised_sumstats_path"], tmp_path)
    loci = read_loci(Path(loci_result["loci_path"]))

    assert loci
    assert list(loci[0]) == LOCUS_OUTPUT_COLUMNS


def test_define_loci_cli_writes_loci_file(tmp_path: Path) -> None:
    qc_result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)
    result = CliRunner().invoke(
        app,
        [
            "define-loci",
            "--gwas",
            qc_result["harmonised_sumstats_path"],
            "--outdir",
            str(tmp_path),
            "--p-threshold",
            "5e-8",
            "--window-kb",
            "500",
        ],
    )

    assert result.exit_code == 0
    assert '"n_loci":' in result.output
    assert (tmp_path / "loci" / "loci.tsv").exists()
