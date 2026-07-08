# Plotting Recipes

These are conventional, reusable plotting recipes for genetics and omics
analyses. They are not novel visualisations. The current MVP documents expected
inputs; plotting commands can be implemented as a future `standard-figures`
interface.

## 1. PCA / Grouping Plot

Question: do samples cluster by phenotype, batch, tissue or cell type?

Required columns:

```text
sample_id, PC1, PC2, group, batch
```

Example command shape:

```bash
drugpipe standard-figures pca --scores pca_scores.tsv --out figures/pca.png
```

Caution: PCA separates major sources of variation, not necessarily biology of
interest.

## 2. Expression By Group

Question: is a candidate gene higher or lower in relevant groups?

Inputs:

```text
expression matrix
metadata: sample_id, group, batch
```

Example:

```bash
drugpipe standard-figures expression-by-group --gene SOST --expression expr.tsv --metadata metadata.tsv --out figures/SOST_expression.png
```

Caution: expression differences do not prove causal target relevance.

## 3. Expression Heatmap

Question: do marker, pathway or candidate genes show coordinated patterns?

Inputs:

```text
expression matrix
selected genes
sample metadata
```

Example:

```bash
drugpipe standard-figures heatmap --expression expr.tsv --genes pathway_genes.txt --out figures/heatmap.png
```

Caution: scaling and gene selection strongly influence visual patterns.

## 4. Volcano Plot

Question: which genes show large and statistically supported expression changes?

Required columns:

```text
gene_name, log2_fold_change, adjusted_p_value
```

Example:

```bash
drugpipe standard-figures volcano --de differential_expression.tsv --out figures/volcano.png
```

Caution: significance depends on model, filtering and multiple-testing control.

## 5. MA Plot

Question: are fold changes dependent on average expression?

Required columns:

```text
mean_expression, log2_fold_change, adjusted_p_value
```

Example:

```bash
drugpipe standard-figures ma --de differential_expression.tsv --out figures/ma.png
```

Caution: low-expression genes can have unstable fold changes.

## 6. Manhattan Plot

Question: where are GWAS association signals across the genome?

Required columns:

```text
SNP, CHR, BP, P
```

Example:

```bash
drugpipe standard-figures manhattan --gwas harmonised_sumstats.tsv.gz --out figures/manhattan.png
```

Caution: genome build, allele harmonisation and variant filtering should be
checked before plotting.

## 7. QQ Plot

Question: are GWAS p-values calibrated, inflated or strongly polygenic?

Required columns:

```text
P
```

Example:

```bash
drugpipe standard-figures qq --gwas harmonised_sumstats.tsv.gz --out figures/qq.png
```

Caution: inflation can reflect confounding, polygenicity or both.

## 8. Enrichment Dotplot

Question: which pathways are enriched among candidate or prioritised genes?

Required columns:

```text
pathway_name, adjusted_p_value, n_genes
```

Example:

```bash
drugpipe standard-figures enrichment-dotplot --results enrichment.tsv --out figures/enrichment.png
```

Caution: pathway databases are redundant and annotation-biased.

## 9. Forest Plot

Question: what are the effect sizes and uncertainty across MR or other effect
estimates?

Required columns:

```text
exposure, outcome, beta, se, p
```

Example:

```bash
drugpipe standard-figures forest --effects mr_results.tsv --out figures/forest.png
```

Caution: compare effect scales and directions before combining results.

## 10. Target Evidence Heatmap

Question: which targets are supported by which evidence layers?

Required columns:

```text
gene_name, genetic_association_score, fine_mapping_score, locus_to_gene_score,
qtl_colocalisation_score, bone_cell_context_score, pathway_context_score,
mr_target_validation_score, druggability_score
```

Example:

```bash
drugpipe standard-figures evidence-heatmap --targets ranked_targets.tsv --out figures/evidence_heatmap.png
```

Caution: heatmaps compare evidence patterns; they should not be interpreted as
independent validation.
