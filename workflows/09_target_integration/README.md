# Target Evidence Integration

## Scientific Question

Which candidate genes have the strongest combined evidence as target
hypotheses?

## When To Use This Step

Use this after the available evidence layers have been imported. Missing
evidence is allowed and receives zero contribution rather than crashing the run.

## Typical Inputs

- locus-gene map
- credible-set summary
- QTL summary
- cell and pathway context
- MR, safety and druggability summaries
- scoring configuration

## Recommended Established Tools

- DrugPipe target scoring
- manual review of top evidence cards
- downstream experimental prioritisation

## Public Data Resources

Use the resources from upstream modules. This step integrates their exported
summary tables.

## Example Workflow

1. Confirm all available evidence tables use the expected schemas.
2. Run target scoring.
3. Generate a Markdown report.
4. Generate target evidence cards.
5. Review evidence summaries and caveats.

## DrugPipe Example

```bash
osteo-target-gwas score-targets --results results/example --config config/default.yaml
osteo-target-gwas report --results results/example --out reports/example/target_prioritisation_report.md
osteo-target-gwas make-target-cards --results results/example --top-n 10 --outdir reports/example/target_cards
```

## Expected Output Schema

```text
rank, gene_name, locus_id, target_score, genetic_association_score,
fine_mapping_score, locus_to_gene_score, qtl_colocalisation_score,
bone_cell_context_score, pathway_context_score, mr_target_validation_score,
druggability_score, phe_mr_safety_penalty, evidence_summary
```

## Interpretation

The target score is a ranking heuristic. It is useful for triage, not a
probability of success.

## Caveats

Weights, missing evidence and annotation bias can influence rank order.
