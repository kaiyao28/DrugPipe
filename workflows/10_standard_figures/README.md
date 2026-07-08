# Standard Plotting Recipes

## Scientific Question

Which conventional plots help inspect GWAS, expression, enrichment, effect-size
and target evidence tables?

## When To Use This Step

Use this after producing small summary tables. These recipes are intended for
quality control, communication and interpretation.

## Typical Inputs

- PCA scores and metadata
- expression matrices and metadata
- differential-expression summaries
- GWAS tables
- enrichment summaries
- MR/effect summaries
- ranked target tables

## Recommended Established Tools

- matplotlib, seaborn or plotnine in Python
- ggplot2 in R
- Scanpy plotting for single-cell objects

## Public Data Resources

Plotting usually consumes outputs from upstream modules rather than raw public
resources.

## Example Workflow

1. Prepare a small plotting input table.
2. Choose a conventional plot type.
3. Check axis labels, scaling and grouping.
4. Save publication- or report-ready files.

## DrugPipe Example

The current MVP documents plotting recipes in `docs/plotting_recipes.md`.
Theme-based plotting modules live under `src/osteo_target_gwas/figures/`.

## Expected Output Schema

See `docs/plotting_recipes.md` for plot-specific input schemas.

## Interpretation

Figures summarise evidence and QC patterns. They do not replace statistical
testing or biological validation.

## Caveats

Visual patterns can be driven by scaling, filtering, batch effects or missing
metadata.
