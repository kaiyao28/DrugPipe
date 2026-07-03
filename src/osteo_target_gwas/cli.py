"""Command-line interface for the osteoporosis target-discovery pipeline."""

from __future__ import annotations

import typer

from osteo_target_gwas import __version__

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
def validate() -> None:
    """Validate pipeline inputs and configuration."""
    _placeholder("validate")


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
