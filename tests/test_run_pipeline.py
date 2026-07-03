import json
from pathlib import Path

from typer.testing import CliRunner

from osteo_target_gwas.cli import app


def test_full_run_completes_on_example_data(tmp_path: Path) -> None:
    outdir = tmp_path / "results" / "example"
    report = tmp_path / "reports" / "example" / "target_prioritisation_report.md"
    cards_dir = tmp_path / "reports" / "example" / "target_cards"

    result = CliRunner().invoke(
        app,
        [
            "run",
            "--gwas",
            "data/example/example_gwas.tsv",
            "--genes",
            "data/example/gene_annotation.tsv",
            "--l2g",
            "data/example/l2g_scores.tsv",
            "--credible-sets",
            "data/example/credible_sets.tsv",
            "--coloc",
            "data/example/coloc_results.tsv",
            "--bone-markers",
            "data/example/bone_cell_markers.tsv",
            "--pathways",
            "data/example/pathway_gene_sets.tsv",
            "--mr",
            "data/example/mr_results.tsv",
            "--mediation",
            "data/example/mediation_mr_results.tsv",
            "--phe-mr",
            "data/example/phe_mr_results.tsv",
            "--druggability",
            "data/example/druggability.tsv",
            "--config",
            "config/default.yaml",
            "--outdir",
            str(outdir),
            "--report",
            str(report),
            "--cards-dir",
            str(cards_dir),
        ],
    )

    assert result.exit_code == 0
    assert (outdir / "targets" / "ranked_targets.tsv").exists()
    assert report.exists()
    assert any(cards_dir.glob("*.md"))

    manifest_path = outdir / "run_manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "validate" in manifest["completed_stages"]
    assert "make-target-cards" in manifest["completed_stages"]
    assert manifest["output_paths"]["ranked_targets"].endswith("ranked_targets.tsv")
