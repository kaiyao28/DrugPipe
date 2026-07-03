"""Command-line interface for the osteoporosis target-discovery pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
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
from osteo_target_gwas.report.target_cards import make_target_cards as run_target_cards
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
def make_target_cards(
    results: Path | None = typer.Option(
        None,
        "--results",
        help="Trait results directory containing ranked targets and evidence outputs.",
        file_okay=False,
    ),
    top_n: int = typer.Option(
        10,
        "--top-n",
        help="Number of top ranked targets to render.",
        min=1,
    ),
    outdir: Path | None = typer.Option(
        None,
        "--outdir",
        help="Directory for Markdown target cards.",
        file_okay=False,
    ),
) -> None:
    """Create target evidence cards."""
    if results is None and outdir is None:
        _placeholder("make-target-cards")
        return
    if results is None or outdir is None:
        typer.echo("Target card generation requires --results and --outdir.", err=True)
        raise typer.Exit(code=1)

    try:
        result = run_target_cards(results_dir=results, outdir=outdir, top_n=top_n)
    except (OSError, TypeError, ValueError) as error:
        typer.echo(f"Target card generation failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(json.dumps({"n_cards": result["n_cards"]}, indent=2))
    typer.echo(f"Wrote target cards to {outdir}")


@app.command("run")
def run(
    gwas: Path | None = typer.Option(
        None,
        "--gwas",
        help="GWAS summary-statistics file.",
        dir_okay=False,
        readable=True,
    ),
    genes: Path | None = typer.Option(
        None,
        "--genes",
        help="Gene annotation TSV.",
        dir_okay=False,
        readable=True,
    ),
    l2g: Path | None = typer.Option(
        None,
        "--l2g",
        help="Optional locus-to-gene score TSV.",
    ),
    credible_sets: Path | None = typer.Option(
        None,
        "--credible-sets",
        help="Optional precomputed credible-set TSV.",
    ),
    coloc_file: Path | None = typer.Option(
        None,
        "--coloc",
        help="Optional precomputed coloc result TSV.",
    ),
    bone_markers: Path | None = typer.Option(
        None,
        "--bone-markers",
        help="Optional bone-cell marker TSV.",
    ),
    pathways: Path | None = typer.Option(
        None,
        "--pathways",
        help="Optional pathway gene-set TSV.",
    ),
    mr: Path | None = typer.Option(
        None,
        "--mr",
        help="Optional target MR result TSV.",
    ),
    mediation: Path | None = typer.Option(
        None,
        "--mediation",
        help="Optional mediation MR result TSV.",
    ),
    phe_mr_file: Path | None = typer.Option(
        None,
        "--phe-mr",
        help="Optional Phe-MR safety scan TSV.",
    ),
    druggability_file: Path | None = typer.Option(
        None,
        "--druggability",
        help="Optional druggability annotation TSV.",
    ),
    config: Path | None = typer.Option(
        None,
        "--config",
        help="Pipeline configuration YAML.",
        dir_okay=False,
        readable=True,
    ),
    outdir: Path | None = typer.Option(
        None,
        "--outdir",
        help="Trait results output directory.",
        file_okay=False,
    ),
    report_path: Path | None = typer.Option(
        None,
        "--report",
        help="Optional Markdown report output path.",
        dir_okay=False,
    ),
    cards_dir: Path | None = typer.Option(
        None,
        "--cards-dir",
        help="Optional output directory for target evidence cards.",
        file_okay=False,
    ),
) -> None:
    """Run the full target-discovery workflow."""
    if (
        gwas is None
        and genes is None
        and config is None
        and outdir is None
        and all(
            path is None
            for path in (
                l2g,
                credible_sets,
                coloc_file,
                bone_markers,
                pathways,
                mr,
                mediation,
                phe_mr_file,
                druggability_file,
                report_path,
                cards_dir,
            )
        )
    ):
        _placeholder("run")
        return

    missing_required = [
        name
        for name, value in {
            "--gwas": gwas,
            "--genes": genes,
            "--config": config,
            "--outdir": outdir,
        }.items()
        if value is None
    ]
    if missing_required:
        typer.echo(f"Run requires {', '.join(missing_required)}.", err=True)
        raise typer.Exit(code=1)

    for label, path in {"--gwas": gwas, "--genes": genes, "--config": config}.items():
        if path is not None and not path.exists():
            typer.echo(f"Run input {label} does not exist: {path}", err=True)
            raise typer.Exit(code=1)

    manifest: dict[str, object] = {
        "command": "osteo-target-gwas run",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_paths": {
            "gwas": str(gwas),
            "genes": str(genes),
            "l2g": _path_or_none(l2g),
            "credible_sets": _path_or_none(credible_sets),
            "coloc": _path_or_none(coloc_file),
            "bone_markers": _path_or_none(bone_markers),
            "pathways": _path_or_none(pathways),
            "mr": _path_or_none(mr),
            "mediation": _path_or_none(mediation),
            "phe_mr": _path_or_none(phe_mr_file),
            "druggability": _path_or_none(druggability_file),
            "config": str(config),
            "outdir": str(outdir),
            "report": _path_or_none(report_path),
            "cards_dir": _path_or_none(cards_dir),
        },
        "output_paths": {},
        "completed_stages": [],
        "skipped_stages": [],
    }

    output_paths = manifest["output_paths"]
    completed_stages = manifest["completed_stages"]
    skipped_stages = manifest["skipped_stages"]

    def complete(stage_name: str, outputs: dict[str, str] | None = None) -> None:
        completed_stages.append(stage_name)
        if outputs:
            output_paths.update(outputs)

    def skip(stage_name: str, reason: str) -> None:
        message = f"Skipping {stage_name}: {reason}"
        typer.echo(f"WARNING: {message}", err=True)
        skipped_stages.append({"stage": stage_name, "reason": reason})

    try:
        _log_stage_start("validate")
        pipeline_config = load_default_config(config)
        mappings = pipeline_config.get("column_mappings", {}).get("gwas_summary_statistics", {})
        rows = read_gwas(gwas, mappings)
        validation_summary = validate_gwas_schema(rows)
        schema_validation_path = outdir / "qc" / "schema_validation.json"
        schema_validation_path.parent.mkdir(parents=True, exist_ok=True)
        schema_validation_path.write_text(json.dumps(validation_summary, indent=2) + "\n", encoding="utf-8")
        complete("validate", {"schema_validation": str(schema_validation_path)})
        _log_stage_done("validate")

        _log_stage_start("qc")
        qc_result = run_gwas_qc(gwas_path=gwas, outdir=outdir, config_path=config)
        complete(
            "qc",
            {
                "harmonised_sumstats": qc_result["harmonised_sumstats_path"],
                "qc_summary": qc_result["qc_summary_path"],
                "qc_report": qc_result["qc_report_path"],
            },
        )
        _log_stage_done("qc")

        _log_stage_start("define-loci")
        loci_result = define_significant_loci(
            gwas_path=qc_result["harmonised_sumstats_path"],
            outdir=outdir,
            config_path=config,
        )
        complete("define-loci", {"loci": loci_result["loci_path"]})
        _log_stage_done("define-loci")

        if _optional_input_available("finemap", credible_sets, skip):
            _log_stage_start("finemap")
            finemap_result = run_finemap_placeholder(
                gwas_path=qc_result["harmonised_sumstats_path"],
                loci_path=loci_result["loci_path"],
                credible_sets_path=credible_sets,
                outdir=outdir,
            )
            complete(
                "finemap",
                {
                    "credible_sets": finemap_result["credible_sets_path"],
                    "locus_finemap_summary": finemap_result["locus_finemap_summary_path"],
                },
            )
            _log_stage_done("finemap")

        _log_stage_start("map-genes")
        gene_result = map_variants_to_genes(
            loci_path=loci_result["loci_path"],
            genes_path=genes,
            l2g_path=l2g if _path_exists(l2g) else None,
            outdir=outdir,
        )
        if l2g is not None and not _path_exists(l2g):
            skip("l2g-import", f"optional input not found: {l2g}")
        complete("map-genes", {"locus_gene_map": gene_result["locus_gene_map_path"]})
        _log_stage_done("map-genes")

        if _optional_input_available("coloc", coloc_file, skip):
            _log_stage_start("coloc")
            coloc_result = run_coloc_parser(coloc_path=coloc_file, outdir=outdir)
            complete(
                "coloc",
                {
                    "coloc_results": coloc_result["coloc_results_path"],
                    "gene_coloc_summary": coloc_result["gene_coloc_summary_path"],
                },
            )
            _log_stage_done("coloc")

        if _optional_input_available("bone-context", bone_markers, skip):
            _log_stage_start("bone-context")
            bone_result = score_bone_cell_context(
                gene_map_path=gene_result["locus_gene_map_path"],
                markers_path=bone_markers,
                outdir=outdir,
            )
            complete("bone-context", {"bone_cell_relevance": bone_result["bone_cell_relevance_path"]})
            _log_stage_done("bone-context")

        if _optional_input_available("pathway", pathways, skip):
            _log_stage_start("pathway")
            pathway_result = annotate_pathway_context(
                gene_map_path=gene_result["locus_gene_map_path"],
                gene_sets_path=pathways,
                outdir=outdir,
            )
            complete(
                "pathway",
                {
                    "gene_pathway_context": pathway_result["gene_pathway_context_path"],
                    "pathway_summary": pathway_result["pathway_summary_path"],
                },
            )
            _log_stage_done("pathway")

        if _optional_input_available("mr-targets", mr, skip):
            _log_stage_start("mr-targets")
            mr_result = run_target_mr_parser(mr_path=mr, outdir=outdir)
            complete(
                "mr-targets",
                {
                    "target_mr_results": mr_result["target_mr_results_path"],
                    "gene_mr_summary": mr_result["gene_mr_summary_path"],
                },
            )
            _log_stage_done("mr-targets")

        if _optional_input_available("mediation-mr", mediation, skip):
            _log_stage_start("mediation-mr")
            mediation_result = run_mediation_mr_parser(mediation_path=mediation, outdir=outdir)
            complete(
                "mediation-mr",
                {
                    "mediation_mr_results": mediation_result["mediation_mr_results_path"],
                    "gene_mediation_summary": mediation_result["gene_mediation_summary_path"],
                },
            )
            _log_stage_done("mediation-mr")

        if _optional_input_available("phe-mr", phe_mr_file, skip):
            _log_stage_start("phe-mr")
            phe_result = run_phe_mr_parser(phe_mr_path=phe_mr_file, outdir=outdir)
            complete(
                "phe-mr",
                {
                    "phe_mr_results": phe_result["phe_mr_results_path"],
                    "gene_phe_mr_safety_summary": phe_result["gene_phe_mr_safety_summary_path"],
                },
            )
            _log_stage_done("phe-mr")

        if _optional_input_available("druggability", druggability_file, skip):
            _log_stage_start("druggability")
            druggability_result = run_druggability_annotation(
                druggability_path=druggability_file,
                outdir=outdir,
            )
            complete("druggability", {"druggability": druggability_result["druggability_path"]})
            _log_stage_done("druggability")

        _log_stage_start("score-targets")
        scoring_result = run_target_scoring(results_dir=outdir, config_path=config)
        complete("score-targets", {"ranked_targets": scoring_result["ranked_targets_path"]})
        _log_stage_done("score-targets")

        if report_path is not None:
            _log_stage_start("report")
            report_result = make_markdown_report(results_dir=outdir, out_path=report_path)
            complete("report", {"report": report_result["report_path"]})
            _log_stage_done("report")
        else:
            skip("report", "optional --report output path was not supplied")

        if cards_dir is not None:
            _log_stage_start("make-target-cards")
            cards_result = run_target_cards(results_dir=outdir, outdir=cards_dir, top_n=10)
            complete("make-target-cards", {"target_cards_dir": str(cards_dir)})
            output_paths["target_cards"] = cards_result["target_card_paths"]
            _log_stage_done("make-target-cards")
        else:
            skip("make-target-cards", "optional --cards-dir output directory was not supplied")

    except (OSError, TypeError, ValueError, NotImplementedError) as error:
        _write_run_manifest(outdir, manifest)
        typer.echo(f"Pipeline failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    manifest_path = _write_run_manifest(outdir, manifest)
    typer.echo(json.dumps({"manifest": str(manifest_path), "completed_stages": completed_stages}, indent=2))


def _log_stage_start(stage_name: str) -> None:
    typer.echo(f"Starting {stage_name}")


def _log_stage_done(stage_name: str) -> None:
    typer.echo(f"Completed {stage_name}")


def _write_run_manifest(outdir: Path, manifest: dict[str, object]) -> Path:
    manifest_path = outdir / "run_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def _path_or_none(path: Path | None) -> str | None:
    return str(path) if path is not None else None


def _path_exists(path: Path | None) -> bool:
    return path is not None and path.exists()


def _optional_input_available(
    stage_name: str,
    path: Path | None,
    skip,
) -> bool:
    if path is None:
        skip(stage_name, "optional input was not supplied")
        return False
    if not path.exists():
        skip(stage_name, f"optional input not found: {path}")
        return False
    return True


if __name__ == "__main__":
    app()
