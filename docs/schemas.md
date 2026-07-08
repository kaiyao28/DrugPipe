# Schemas

DrugPipe schemas are deliberately small TSV-style contracts. Column names are
case-sensitive unless a command explicitly supports configurable mappings.

## GWAS Summary Statistics

Required columns:

```text
SNP, CHR, BP, A1, A2, BETA, SE, P, EAF, N
```

Optional columns:

```text
INFO, OR, N_CASE, N_CONTROL
```

Validation rules include p-values and allele frequencies between 0 and 1,
alleles in A/C/G/T, chromosomes 1-22/X/Y/MT, positive base positions and
positive sample size.

## Gene Annotation

Required columns:

```text
gene_id, gene_name, chr, start, end, tss, strand, gene_type
```

Coordinates should match the GWAS genome build. TSS is used for nearest-gene
distance.

## L2G Scores

Required columns:

```text
locus_id, gene_name, l2g_score, l2g_evidence_type
```

`l2g_score` should be between 0 and 1.

## Credible Sets

Required columns:

```text
locus_id, SNP, CHR, BP, PIP, credible_set, method
```

`PIP` must be between 0 and 1.

## Colocalisation Results

Required columns:

```text
locus_id, gene_name, qtl_type, tissue_or_cell, pp_h4, pp_h3, effect_direction
```

`pp_h4` and `pp_h3` must be between 0 and 1. Supported QTL types are eQTL,
sQTL, pQTL, caQTL and other.

## Bone Cell Markers

Required columns:

```text
gene_name, cell_type, marker_strength
```

Supported cell types include osteoblast, osteoclast, osteocyte,
mesenchymal_stromal_cell and immune_cell. `marker_strength` should be scaled
between 0 and 1.

## Pathway Gene Sets

Required columns:

```text
pathway_name, gene_name
```

## MR Results

Required columns:

```text
gene_name, exposure_type, exposure_id, outcome, beta, se, p, f_statistic, method, direction
```

`se` must be positive, `p` must be between 0 and 1 and `f_statistic` must be
non-negative.

## Mediation MR Results

Required columns:

```text
gene_name, mediator, mediator_category, indirect_effect, se, p, proportion_mediated
```

`proportion_mediated` must be between 0 and 1.

## Phe-MR Results

Required columns:

```text
gene_name, outcome_trait, beta, se, p, category, safety_flag
```

Supported safety flags are none, monitor, liability, protective and unknown.

## Druggability

Required columns:

```text
gene_name, target_class, tractability_modality, tractability_score, known_drug, known_drug_name, safety_note
```

`tractability_score` must be between 0 and 1. `known_drug` is parsed as a
boolean-like value.

## Ranked Targets

Key output columns:

```text
rank, gene_name, locus_id, target_score, genetic_association_score,
fine_mapping_score, locus_to_gene_score, qtl_colocalisation_score,
bone_cell_context_score, pathway_context_score, mr_target_validation_score,
mediation_score, druggability_score, phe_mr_safety_penalty,
annotation_bias_penalty, evidence_summary
```
