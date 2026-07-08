# Interpretation Guide

DrugPipe ranks target hypotheses by integrating evidence. The score is a
prioritisation heuristic, not a probability of success.

## 1. GWAS Association

A lead SNP is the most significant variant in a locus. Key fields are p-value,
effect size, standard error, allele frequency, sample size and genomic position.
Always record genome build, ancestry and phenotype definition.

The locus window is a practical region around an association signal. It does not
guarantee that the causal variant or effector gene lies inside the chosen
window.

## 2. Fine-Mapping

PIP is posterior inclusion probability for a variant under a fine-mapping model.
A credible set is a group of variants whose cumulative posterior probability
passes a chosen threshold.

Interpretation depends on LD quality, ancestry matching, variant coverage and
model assumptions. Credible-set purity can help flag diffuse or poorly resolved
signals.

## 3. Locus-To-Gene Mapping

DrugPipe can use nearest gene, overlapping gene and imported L2G-style scores.
Nearest gene alone is weak evidence. Stronger hypotheses combine proximity with
fine-mapping, QTL, coding consequence, chromatin, pathway and cell-context
evidence.

## 4. QTL Colocalisation

PP_H4 supports a shared causal signal between GWAS and QTL evidence. PP_H3
supports distinct causal signals in the same region. Tissue or cell relevance is
central for interpretation.

High PP_H4 supports a gene-linking hypothesis but does not define therapeutic
direction by itself.

## 5. Expression And Cell Context

Expression specificity and marker strength can indicate whether a candidate gene
is active in relevant cells. PCA/grouping plots and expression-by-group plots
can reveal sample structure, outliers or broad cell-type patterns.

Expression does not prove causality; it is context evidence.

## 6. Pathway Evidence

Pathway annotations support mechanism interpretation. ORA/GSEA-style results can
highlight biology shared across candidate genes.

Pathways are redundant and annotation-biased, so they should not dominate target
ranking without genetic or molecular support.

## 7. Mendelian Randomisation

MR summaries include beta, standard error, p-value, method, direction and
instrument strength. The F-statistic helps flag weak instruments.

MR evidence depends on valid instruments, limited horizontal pleiotropy,
appropriate outcome selection and careful directionality checks.

## 8. Phe-MR And Safety

Phe-MR scans can flag possible liability, monitoring or protective traits.
Interpret results with multiple testing, phenotype quality and instrument
specificity in mind.

Absence of a flag is not proof of safety.

## 9. Druggability

Tractability reflects whether a target class and modality may be feasible.
Known drug status, target class and safety notes can help prioritise follow-up.

Druggability does not equal clinical feasibility.

## 10. Target Score

The target score combines genetic association, fine-mapping, locus-to-gene, QTL,
bone context, pathway, MR, druggability and penalty terms. It is intended to
rank hypotheses for review and follow-up experiments.
