"""Command-line interface for the osteoporosis target-discovery pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from osteo_target_gwas import __version__
from osteo_target_gwas.config import load_default_config
from osteo_target_gwas.io.read_gwas import read_gwas
from osteo_target_gwas.io.validate_schema import validate_gwas_schema

app = typer.Typer(
    help=(
        "Run a reproducible osteoporosis post-GWAS target-discovery pipeline "
        "from GWAS summary statistics to prioritised target evidence cards."
    )
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"osteo-target-gwas {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the package version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Coordinate osteoporosis post-GWAS target-discovery stages."""


def _placeholder(command_name: str) -> None:
    typer.echo(f"The '{command_name}' command exists but is not implemented yet.")


@app.command("validate")
def validate(
    gwas: Path | None = typer.Option(
        None,
        "--gwas",
        help="GWAS summary-statistics file to validate.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    config: Path = typer.Option(
        Path("config/default.yaml"),
        "--config",
        help="Pipeline configuration YAML with GWAS column mappings.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    outdir: Path | None = typer.Option(
        None,
        "--outdir",
        help="Optional output directory for schema_validation.json.",
        file_okay=False,
    ),
) -> None:
    """Validate pipeline inputs and configuration."""
    if gwas is None:
        _placeholder("validate")
        return

    try:
        pipeline_config = load_default_config(config)
        mappings = pipeline_config.get("column_mappings", {}).get("gwas_summary_statistics", {})
        rows = read_gwas(gwas, mappings)
        summary = validate_gwas_schema(rows)
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Validation failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps(summary, indent=2))

    if outdir is not None:
        output_path = outdir / "qc" / "schema_validation.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        typer.echo(f"Wrote validation summary to {output_path}")


@app.command("qc")
def qc() -> None:
    """Run GWAS summary-statistic quality control."""
    _placeholder("qc")


@app.command("define-loci")
def define_loci() -> None:
    """Define associated loci from GWAS results."""
    _placeholder("define-loci")


@app.command("finemap")
def finemap() -> None:
    """Prepare fine-mapping-ready credible-set inputs."""
    _placeholder("finemap")


@app.command("map-genes")
def map_genes() -> None:
    """Map variants and loci to candidate genes."""
    _placeholder("map-genes")


@app.command("coloc")
def coloc() -> None:
    """Collect QTL colocalisation evidence."""
    _placeholder("coloc")


@app.command("bone-context")
def bone_context() -> None:
    """Add bone-cell and tissue-context evidence."""
    _placeholder("bone-context")


@app.command("pathway")
def pathway() -> None:
    """Interpret pathways and biological mechanisms."""
    _placeholder("pathway")


@app.command("mr-targets")
def mr_targets() -> None:
    """Run genome-wide Mendelian randomisation target scans."""
    _placeholder("mr-targets")


@app.command("mediation-mr")
def mediation_mr() -> None:
    """Run mediation Mendelian randomisation analyses."""
    _placeholder("mediation-mr")


@app.command("phe-mr")
def phe_mr() -> None:
    """Run phenome-wide Mendelian randomisation safety scans."""
    _placeholder("phe-mr")


@app.command("druggability")
def druggability() -> None:
    """Annotate candidate-target druggability."""
    _placeholder("druggability")


@app.command("score-targets")
def score_targets() -> None:
    """Score and rank candidate targets."""
    _placeholder("score-targets")


@app.command("report")
def report() -> None:
    """Build pipeline-level reports."""
    _placeholder("report")


@app.command("make-target-cards")
def make_target_cards() -> None:
    """Create target evidence cards."""
    _placeholder("make-target-cards")


@app.command("run")
def run() -> None:
    """Run the full target-discovery workflow."""
    _placeholder("run")


if __name__ == "__main__":
    app()
