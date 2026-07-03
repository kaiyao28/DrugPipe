import csv
from pathlib import Path

from typer.testing import CliRunner

from osteo_target_gwas.cli import app
from osteo_target_gwas.targets.druggability import (
    read_druggability,
    run_druggability_annotation,
)


EXAMPLE_DRUGGABILITY = Path("data/example/druggability.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_druggability_file_parses() -> None:
    rows = read_druggability(EXAMPLE_DRUGGABILITY)

    assert rows
    assert "druggability_score" in rows[0]
    assert rows[0]["safety_note"]


def test_known_drug_bonus_applies() -> None:
    rows = read_druggability(EXAMPLE_DRUGGABILITY)
    sost = next(row for row in rows if row["gene_name"] == "SOST")

    assert sost["known_drug"] == "true"
    assert float(sost["druggability_score"]) == 1.0


def test_druggability_score_capped_at_one(tmp_path: Path) -> None:
    path = tmp_path / "druggability.tsv"
    write_tsv(
        path,
        [
            {
                "gene_name": "CAP1",
                "target_class": "enzyme",
                "tractability_modality": "small_molecule",
                "tractability_score": "0.97",
                "known_drug": "yes",
                "known_drug_name": "synthetic_reference",
                "safety_note": "synthetic note",
            }
        ],
    )

    rows = read_druggability(path)

    assert rows[0]["druggability_score"] == "1"


def test_druggability_output_created(tmp_path: Path) -> None:
    result = run_druggability_annotation(EXAMPLE_DRUGGABILITY, tmp_path)
    output_path = Path(result["druggability_path"])

    assert output_path.exists()
    assert read_tsv(output_path)


def test_druggability_cli_writes_output(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "druggability",
            "--druggability",
            str(EXAMPLE_DRUGGABILITY),
            "--outdir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert '"n_targets":' in result.output
    assert (tmp_path / "targets" / "druggability.tsv").exists()
