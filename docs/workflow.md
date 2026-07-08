# Workflow

DrugPipe is a modular post-GWAS target-discovery workflow and reference code
library. It does not assume that every analysis can or should run in one Python
process.

Real studies often run intensive analyses independently:

```text
GWAS on appropriate compute
  -> locus table
fine-mapping with external LD
  -> credible_sets.tsv
QTL colocalisation
  -> coloc_results.tsv
expression and cell-context analysis
  -> marker or expression summaries
MR and safety scans
  -> MR/Phe-MR summaries
target annotation
  -> druggability table
DrugPipe
  -> ranked targets, report and evidence cards
```

## Analysis Modules

| Goal | Module |
| --- | --- |
| GWAS QC and loci | `workflows/01_gwas_qc` |
| map loci to genes | `workflows/02_locus_to_gene` |
| interpret fine-mapping | `workflows/03_finemapping` |
| integrate QTL evidence | `workflows/04_qtl_colocalisation` |
| analyse expression/cell context | `workflows/05_expression_cell_context` |
| pathway analysis | `workflows/06_pathway_enrichment` |
| MR target validation | `workflows/07_mr_target_validation` |
| safety/druggability | `workflows/08_safety_druggability` |
| integrate target evidence | `workflows/09_target_integration` |
| make standard figures | `workflows/10_standard_figures` |

## Summary Tables

The interface between modules is a set of small summary tables. DrugPipe
validates and integrates those tables rather than owning every upstream method.
See `docs/schemas.md` for required columns.

## Toy Demonstration

The synthetic example still runs end to end for testing and onboarding:

```bash
make demo
```

Treat this as a toy integration test, not a claim that real analyses should use
a single command.
