import csv
from pathlib import Path

import pytest
from typer.testing import CliRunner

from osteo_target_gwas.cli import app
from osteo_target_gwas.finemap.parse_credible_sets import (
    read_credible_sets,
    summarise_finemap_by_locus,
)
from osteo_target_gwas.finemap.run_susie_placeholder import run_finemap_placeholder
from osteo_target_gwas.loci.define_loci import define_significant_loci
from osteo_target_gwas.qc.filter_sumstats import run_gwas_qc


EXAMPLE_GWAS = Path("data/example/example_gwas.tsv")
EXAMPLE_CREDIBLE_SETS = Path("data/example/credible_sets.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def prepare_qc_and_loci(tmp_path: Path) -> tuple[str, str]:
    qc_result = run_gwas_qc(EXAMPLE_GWAS, tmp_path)
    loci_result = define_significant_loci(qc_result["harmonised_sumstats_path"], tmp_path)
    return qc_result["harmonised_sumstats_path"], loci_result["loci_path"]


def test_parser_reads_example_credible_sets() -> None:
    rows = read_credible_sets(EXAMPLE_CREDIBLE_SETS)

    assert rows
    assert rows[0]["locus_id"]
    assert 0 <= float(rows[0]["PIP"]) <= 1


def test_invalid_pip_fails(tmp_path: Path) -> None:
    rows = read_tsv(EXAMPLE_CREDIBLE_SETS)
    rows[0]["PIP"] = "1.4"
    invalid_path = tmp_path / "invalid_credible_sets.tsv"
    write_tsv(invalid_path, rows)

    with pytest.raises(ValueError, match="Invalid PIP"):
        read_credible_sets(invalid_path)


def test_locus_finemap_score_is_max_pip() -> None:
    rows = read_credible_sets(EXAMPLE_CREDIBLE_SETS)
    summaries = summarise_finemap_by_locus(rows)
    first_locus = summaries[0]["locus_id"]
    expected = max(float(row["PIP"]) for row in rows if row["locus_id"] == first_locus)

    assert float(summaries[0]["locus_finemap_score"]) == expected


def test_summary_output_created(tmp_path: Path) -> None:
    gwas_path, loci_path = prepare_qc_and_loci(tmp_path)
    result = run_finemap_placeholder(
        gwas_path=gwas_path,
        loci_path=loci_path,
        credible_sets_path=EXAMPLE_CREDIBLE_SETS,
        outdir=tmp_path,
    )

    assert Path(result["credible_sets_path"]).exists()
    assert Path(result["locus_finemap_summary_path"]).exists()
    assert read_tsv(Path(result["locus_finemap_summary_path"]))


def test_missing_credible_sets_raises_not_implemented(tmp_path: Path) -> None:
    gwas_path, loci_path = prepare_qc_and_loci(tmp_path)

    with pytest.raises(NotImplementedError, match="Real SuSiE/FINEMAP wrapping is not implemented"):
        run_finemap_placeholder(gwas_path=gwas_path, loci_path=loci_path, outdir=tmp_path)


def test_finemap_cli_writes_outputs(tmp_path: Path) -> None:
    gwas_path, loci_path = prepare_qc_and_loci(tmp_path)
    result = CliRunner().invoke(
        app,
        [
            "finemap",
            "--gwas",
            gwas_path,
            "--loci",
            loci_path,
            "--credible-sets",
            str(EXAMPLE_CREDIBLE_SETS),
            "--outdir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert '"n_loci":' in result.output
    assert (tmp_path / "finemap" / "credible_sets.tsv").exists()
    assert (tmp_path / "finemap" / "locus_finemap_summary.tsv").exists()
