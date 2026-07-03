import csv
import gzip
from pathlib import Path

import pytest
from typer.testing import CliRunner

from osteo_target_gwas.cli import app
from osteo_target_gwas.config import load_default_config
from osteo_target_gwas.io.read_gwas import read_gwas
from osteo_target_gwas.io.validate_schema import validate_gwas_schema


EXAMPLE_GWAS = Path("data/example/example_gwas.tsv")


def gwas_mappings() -> dict[str, str]:
    config = load_default_config()
    return config["column_mappings"]["gwas_summary_statistics"]


def read_example_rows() -> list[dict[str, str]]:
    with EXAMPLE_GWAS.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_example_gwas_validates() -> None:
    rows = read_gwas(EXAMPLE_GWAS, gwas_mappings())
    summary = validate_gwas_schema(rows)

    assert summary["valid"] is True
    assert summary["row_count"] >= 60
    assert summary["optional_columns_present"] == ["INFO"]


def test_invalid_allele_fails(tmp_path: Path) -> None:
    rows = read_example_rows()
    rows[0]["A1"] = "I"
    path = tmp_path / "invalid_allele.tsv"
    write_tsv(path, rows)

    with pytest.raises(ValueError, match="Invalid A1"):
        validate_gwas_schema(read_gwas(path, gwas_mappings()))


def test_invalid_p_value_fails(tmp_path: Path) -> None:
    rows = read_example_rows()
    rows[0]["P"] = "1.5"
    path = tmp_path / "invalid_p.tsv"
    write_tsv(path, rows)

    with pytest.raises(ValueError, match="Invalid P"):
        validate_gwas_schema(read_gwas(path, gwas_mappings()))


def test_missing_required_column_fails(tmp_path: Path) -> None:
    rows = read_example_rows()
    rows_without_se = [{key: value for key, value in row.items() if key != "SE"} for row in rows]
    path = tmp_path / "missing_se.tsv"
    write_tsv(path, rows_without_se)

    with pytest.raises(ValueError, match="missing required columns.*SE"):
        read_gwas(path, gwas_mappings())


def test_gzipped_input_can_be_read(tmp_path: Path) -> None:
    gzipped_path = tmp_path / "example_gwas.tsv.gz"
    gzipped_path.write_bytes(gzip.compress(EXAMPLE_GWAS.read_bytes()))

    rows = read_gwas(gzipped_path, gwas_mappings())
    summary = validate_gwas_schema(rows)

    assert summary["valid"] is True
    assert summary["row_count"] >= 60


def test_validate_cli_prints_summary_and_writes_json(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "validate",
            "--gwas",
            str(EXAMPLE_GWAS),
            "--config",
            "config/default.yaml",
            "--outdir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert '"valid": true' in result.output
    assert (tmp_path / "qc" / "schema_validation.json").exists()
