"""Command-line interface for the osteoporosis target-discovery pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from osteo_target_gwas import __version__
from osteo_target_gwas.config import load_default_config
from osteo_target_gwas.finemap.run_susie_placeholder import run_finemap_placeholder
from osteo_target_gwas.genes.variant_to_gene import map_variants_to_genes
from osteo_target_gwas.io.read_gwas import read_gwas
from osteo_target_gwas.io.validate_schema import validate_gwas_schema
from osteo_target_gwas.loci.define_loci import define_significant_loci
from osteo_target_gwas.qc.filter_sumstats import run_gwas_qc
from osteo_target_gwas.qtl.coloc import run_coloc_parser

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
def qc(
    gwas: Path | None = typer.Option(
        None,
        "--gwas",
        help="GWAS summary-statistics file to QC.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    outdir: Path = typer.Option(
        Path("results/example"),
        "--outdir",
        help="Trait output directory; QC files are written under its qc/ subdirectory.",
        file_okay=False,
    ),
    config: Path = typer.Option(
        Path("config/default.yaml"),
        "--config",
        help="Pipeline configuration YAML.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    min_info: float | None = typer.Option(
        None,
        "--min-info",
        help="Minimum imputation INFO score; defaults to config.",
    ),
    min_maf: float | None = typer.Option(
        None,
        "--min-maf",
        help="Minimum minor allele frequency; defaults to config.",
    ),
    remove_ambiguous: bool | None = typer.Option(
        None,
        "--remove-ambiguous/--keep-ambiguous",
        help="Remove A/T and C/G SNPs; defaults to config.",
    ),
) -> None:
    """Run GWAS summary-statistic quality control."""
    if gwas is None:
        _placeholder("qc")
        return

    try:
        result = run_gwas_qc(
            gwas_path=gwas,
            outdir=outdir,
            config_path=config,
            min_info=min_info,
            min_maf=min_maf,
            remove_ambiguous=remove_ambiguous,
        )
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"QC failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps(result["summary"], indent=2))
    typer.echo(f"Wrote harmonised summary statistics to {result['harmonised_sumstats_path']}")
    typer.echo(f"Wrote QC summary to {result['qc_summary_path']}")
    typer.echo(f"Wrote QC report to {result['qc_report_path']}")


@app.command("define-loci")
def define_loci(
    gwas: Path | None = typer.Option(
        None,
        "--gwas",
        help="Harmonised GWAS summary-statistics file.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    outdir: Path = typer.Option(
        Path("results/example"),
        "--outdir",
        help="Trait output directory; loci.tsv is written under its loci/ subdirectory.",
        file_okay=False,
    ),
    config: Path = typer.Option(
        Path("config/default.yaml"),
        "--config",
        help="Pipeline configuration YAML.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    p_threshold: float | None = typer.Option(
        None,
        "--p-threshold",
        help="Genome-wide significance threshold; defaults to config.",
    ),
    window_kb: int | None = typer.Option(
        None,
        "--window-kb",
        help="Lead-SNP window size in kilobases; defaults to config.",
    ),
) -> None:
    """Define associated loci from GWAS results."""
    if gwas is None:
        _placeholder("define-loci")
        return

    try:
        result = define_significant_loci(
            gwas_path=gwas,
            outdir=outdir,
            config_path=config,
            p_threshold=p_threshold,
            window_kb=window_kb,
        )
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Locus definition failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_loci": result["n_loci"], "n_significant_variants": result["n_significant_variants"]}, indent=2))
    typer.echo(f"Wrote loci to {result['loci_path']}")


@app.command("finemap")
def finemap(
    gwas: Path | None = typer.Option(
        None,
        "--gwas",
        help="Harmonised GWAS summary-statistics file.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    loci: Path | None = typer.Option(
        None,
        "--loci",
        help="Locus definition TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    credible_sets: Path | None = typer.Option(
        None,
        "--credible-sets",
        help="Precomputed credible-set TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    outdir: Path = typer.Option(
        Path("results/example"),
        "--outdir",
        help="Trait output directory; fine-mapping files are written under its finemap/ subdirectory.",
        file_okay=False,
    ),
) -> None:
    """Prepare fine-mapping-ready credible-set inputs."""
    if gwas is None and loci is None and credible_sets is None:
        _placeholder("finemap")
        return
    if gwas is None or loci is None:
        typer.echo("Fine-mapping requires --gwas and --loci.", err=True)
        raise typer.Exit(code=1)

    try:
        result = run_finemap_placeholder(
            gwas_path=gwas,
            loci_path=loci,
            outdir=outdir,
            credible_sets_path=credible_sets,
        )
    except NotImplementedError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Fine-mapping failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_loci": result["n_loci"], "n_credible_set_variants": result["n_credible_set_variants"]}, indent=2))
    typer.echo(f"Wrote credible sets to {result['credible_sets_path']}")
    typer.echo(f"Wrote locus fine-mapping summary to {result['locus_finemap_summary_path']}")


@app.command("map-genes")
def map_genes(
    loci: Path | None = typer.Option(
        None,
        "--loci",
        help="Locus definition TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    genes: Path | None = typer.Option(
        None,
        "--genes",
        help="Gene annotation TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    l2g: Path | None = typer.Option(
        None,
        "--l2g",
        help="Optional precomputed locus-to-gene score TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    outdir: Path = typer.Option(
        Path("results/example"),
        "--outdir",
        help="Trait output directory; gene mapping files are written under its genes/ subdirectory.",
        file_okay=False,
    ),
) -> None:
    """Map variants and loci to candidate genes."""
    if loci is None and genes is None and l2g is None:
        _placeholder("map-genes")
        return
    if loci is None or genes is None:
        typer.echo("Gene mapping requires --loci and --genes.", err=True)
        raise typer.Exit(code=1)

    try:
        result = map_variants_to_genes(
            loci_path=loci,
            genes_path=genes,
            l2g_path=l2g,
            outdir=outdir,
        )
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Gene mapping failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_loci": result["n_loci"], "n_gene_links": result["n_gene_links"]}, indent=2))
    typer.echo(f"Wrote locus-to-gene map to {result['locus_gene_map_path']}")


@app.command("coloc")
def coloc(
    coloc_file: Path | None = typer.Option(
        None,
        "--coloc",
        help="Precomputed QTL colocalisation result TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    outdir: Path = typer.Option(
        Path("results/example"),
        "--outdir",
        help="Trait output directory; coloc files are written under its qtl/ subdirectory.",
        file_okay=False,
    ),
) -> None:
    """Collect QTL colocalisation evidence."""
    if coloc_file is None:
        _placeholder("coloc")
        return

    try:
        result = run_coloc_parser(coloc_path=coloc_file, outdir=outdir)
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Colocalisation parsing failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_coloc_records": result["n_coloc_records"], "n_genes": result["n_genes"]}, indent=2))
    typer.echo(f"Wrote coloc results to {result['coloc_results_path']}")
    typer.echo(f"Wrote gene coloc summary to {result['gene_coloc_summary_path']}")


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
