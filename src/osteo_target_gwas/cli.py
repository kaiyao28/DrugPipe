"""Command-line interface for the osteoporosis target-discovery pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from osteo_target_gwas import __version__
from osteo_target_gwas.biology.bone_cell_context import score_bone_cell_context
from osteo_target_gwas.biology.pathway import annotate_pathway_context
from osteo_target_gwas.config import load_default_config
from osteo_target_gwas.finemap.run_susie_placeholder import run_finemap_placeholder
from osteo_target_gwas.genes.variant_to_gene import map_variants_to_genes
from osteo_target_gwas.io.read_gwas import read_gwas
from osteo_target_gwas.io.validate_schema import validate_gwas_schema
from osteo_target_gwas.loci.define_loci import define_significant_loci
from osteo_target_gwas.mr.mediation import run_mediation_mr_parser
from osteo_target_gwas.mr.phe_mr import run_phe_mr_parser
from osteo_target_gwas.mr.target_mr import run_target_mr_parser
from osteo_target_gwas.qc.filter_sumstats import run_gwas_qc
from osteo_target_gwas.qtl.coloc import run_coloc_parser
from osteo_target_gwas.report.make_report import make_markdown_report
from osteo_target_gwas.targets.druggability import run_druggability_annotation
from osteo_target_gwas.targets.score import score_targets as run_target_scoring

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
def bone_context(
    gene_map: Path | None = typer.Option(
        None,
        "--gene-map",
        help="Locus-to-gene map TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    markers: Path | None = typer.Option(
        None,
        "--markers",
        help="Bone-cell marker TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    outdir: Path = typer.Option(
        Path("results/example"),
        "--outdir",
        help="Trait output directory; cell-context files are written under its cell_context/ subdirectory.",
        file_okay=False,
    ),
) -> None:
    """Add bone-cell and tissue-context evidence."""
    if gene_map is None and markers is None:
        _placeholder("bone-context")
        return
    if gene_map is None or markers is None:
        typer.echo("Bone-cell context scoring requires --gene-map and --markers.", err=True)
        raise typer.Exit(code=1)

    try:
        result = score_bone_cell_context(
            gene_map_path=gene_map,
            markers_path=markers,
            outdir=outdir,
        )
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Bone-cell context scoring failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_genes": result["n_genes"]}, indent=2))
    typer.echo(f"Wrote bone-cell relevance to {result['bone_cell_relevance_path']}")


@app.command("pathway")
def pathway(
    gene_map: Path | None = typer.Option(
        None,
        "--gene-map",
        help="Locus-to-gene map TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    gene_sets: Path | None = typer.Option(
        None,
        "--gene-sets",
        help="Pathway gene-set TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    outdir: Path = typer.Option(
        Path("results/example"),
        "--outdir",
        help="Trait output directory; pathway files are written under its biology/ subdirectory.",
        file_okay=False,
    ),
) -> None:
    """Interpret pathways and biological mechanisms."""
    if gene_map is None and gene_sets is None:
        _placeholder("pathway")
        return
    if gene_map is None or gene_sets is None:
        typer.echo("Pathway annotation requires --gene-map and --gene-sets.", err=True)
        raise typer.Exit(code=1)

    try:
        result = annotate_pathway_context(
            gene_map_path=gene_map,
            gene_sets_path=gene_sets,
            outdir=outdir,
        )
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Pathway annotation failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_genes": result["n_genes"], "n_pathways": result["n_pathways"]}, indent=2))
    typer.echo(f"Wrote gene pathway context to {result['gene_pathway_context_path']}")
    typer.echo(f"Wrote pathway summary to {result['pathway_summary_path']}")


@app.command("mr-targets")
def mr_targets(
    mr: Path | None = typer.Option(
        None,
        "--mr",
        help="Precomputed target MR result TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    outdir: Path = typer.Option(
        Path("results/example"),
        "--outdir",
        help="Trait output directory; MR files are written under its mr/ subdirectory.",
        file_okay=False,
    ),
) -> None:
    """Run genome-wide Mendelian randomisation target scans."""
    if mr is None:
        _placeholder("mr-targets")
        return

    try:
        result = run_target_mr_parser(mr_path=mr, outdir=outdir)
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Target MR parsing failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_mr_records": result["n_mr_records"], "n_genes": result["n_genes"]}, indent=2))
    typer.echo(f"Wrote target MR results to {result['target_mr_results_path']}")
    typer.echo(f"Wrote gene MR summary to {result['gene_mr_summary_path']}")


@app.command("mediation-mr")
def mediation_mr(
    mediation: Path | None = typer.Option(
        None,
        "--mediation",
        help="Precomputed mediation MR result TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    outdir: Path = typer.Option(
        Path("results/example"),
        "--outdir",
        help="Trait output directory; mediation MR files are written under its mr/ subdirectory.",
        file_okay=False,
    ),
) -> None:
    """Run mediation Mendelian randomisation analyses."""
    if mediation is None:
        _placeholder("mediation-mr")
        return

    try:
        result = run_mediation_mr_parser(mediation_path=mediation, outdir=outdir)
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Mediation MR parsing failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_mediation_records": result["n_mediation_records"], "n_genes": result["n_genes"]}, indent=2))
    typer.echo(f"Wrote mediation MR results to {result['mediation_mr_results_path']}")
    typer.echo(f"Wrote gene mediation summary to {result['gene_mediation_summary_path']}")


@app.command("phe-mr")
def phe_mr(
    phe_mr_file: Path | None = typer.Option(
        None,
        "--phe-mr",
        help="Precomputed Phe-MR safety scan TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    outdir: Path = typer.Option(
        Path("results/example"),
        "--outdir",
        help="Trait output directory; Phe-MR files are written under its mr/ subdirectory.",
        file_okay=False,
    ),
) -> None:
    """Run phenome-wide Mendelian randomisation safety scans."""
    if phe_mr_file is None:
        _placeholder("phe-mr")
        return

    try:
        result = run_phe_mr_parser(phe_mr_path=phe_mr_file, outdir=outdir)
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Phe-MR parsing failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_phe_mr_records": result["n_phe_mr_records"], "n_genes": result["n_genes"]}, indent=2))
    typer.echo(f"Wrote Phe-MR results to {result['phe_mr_results_path']}")
    typer.echo(f"Wrote gene Phe-MR safety summary to {result['gene_phe_mr_safety_summary_path']}")


@app.command("druggability")
def druggability(
    druggability_file: Path | None = typer.Option(
        None,
        "--druggability",
        help="Druggability and tractability annotation TSV.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    outdir: Path = typer.Option(
        Path("results/example"),
        "--outdir",
        help="Trait output directory; druggability files are written under its targets/ subdirectory.",
        file_okay=False,
    ),
) -> None:
    """Annotate candidate-target druggability."""
    if druggability_file is None:
        _placeholder("druggability")
        return

    try:
        result = run_druggability_annotation(
            druggability_path=druggability_file,
            outdir=outdir,
        )
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Druggability annotation failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_targets": result["n_targets"]}, indent=2))
    typer.echo(f"Wrote druggability annotations to {result['druggability_path']}")


@app.command("score-targets")
def score_targets(
    results: Path | None = typer.Option(
        None,
        "--results",
        help="Trait results directory containing pipeline evidence outputs.",
        file_okay=False,
    ),
    config: Path = typer.Option(
        Path("config/default.yaml"),
        "--config",
        help="Pipeline configuration YAML with scoring weights.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
) -> None:
    """Score and rank candidate targets."""
    if results is None:
        _placeholder("score-targets")
        return

    try:
        result = run_target_scoring(results_dir=results, config_path=config)
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Target scoring failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_targets": result["n_targets"]}, indent=2))
    typer.echo(f"Wrote ranked targets to {result['ranked_targets_path']}")


@app.command("report")
def report(
    results: Path | None = typer.Option(
        None,
        "--results",
        help="Trait results directory containing pipeline evidence outputs.",
        file_okay=False,
    ),
    out: Path | None = typer.Option(
        None,
        "--out",
        help="Markdown report output path.",
        dir_okay=False,
    ),
) -> None:
    """Build pipeline-level reports."""
    if results is None and out is None:
        _placeholder("report")
        return
    if results is None or out is None:
        typer.echo("Report generation requires --results and --out.", err=True)
        raise typer.Exit(code=1)

    try:
        result = make_markdown_report(results_dir=results, out_path=out)
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Report generation failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_ranked_targets": result["n_ranked_targets"]}, indent=2))
    typer.echo(f"Wrote report to {result['report_path']}")


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
