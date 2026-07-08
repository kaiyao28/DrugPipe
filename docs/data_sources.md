# Data Sources

DrugPipe expects summary-level tables. It does not download large public
resources into the repository. For real analyses, obtain or generate the files
below, convert them to the documented schemas, then import them into the
pipeline.

## 1. GWAS Summary Statistics

| Resource | Purpose | Access mode | DrugPipe table |
| --- | --- | --- | --- |
| [GWAS Catalog](https://www.ebi.ac.uk/gwas/downloads) | Published GWAS metadata and available summary statistics | direct downloads and study pages | GWAS summary statistics |
| [GEFOS](http://www.gefos.org/) | Bone mineral density, fracture and osteoporosis studies | study-specific downloads | GWAS summary statistics |
| [OpenGWAS](https://gwas.mrcieu.ac.uk/) | Harmonised GWAS summary statistics for MR workflows | API and web interface | GWAS summary statistics |

Expected columns:

```text
SNP, CHR, BP, A1, A2, BETA, SE, P, EAF, N
```

Interpretation notes: document genome build, ancestry, sample size, imputation
quality and phenotype definition before defining loci.

## 2. Gene Annotation

| Resource | Purpose | Access mode | DrugPipe table |
| --- | --- | --- | --- |
| [Ensembl BioMart](https://www.ensembl.org/biomart) | Gene coordinates and identifiers | web export and API | gene annotation |
| [GENCODE](https://www.gencodegenes.org/) | Reference gene annotation | direct downloads | gene annotation |

Expected columns:

```text
gene_id, gene_name, chr, start, end, tss, strand, gene_type
```

Coordinates should use the same genome build as the GWAS input.

## 3. Fine-Mapping / Credible Sets

| Resource or tool | Purpose | Access mode | DrugPipe table |
| --- | --- | --- | --- |
| SuSiE | Fine-mapping with summary statistics and LD | generated externally | credible sets |
| FINEMAP | Bayesian fine-mapping | generated externally | credible sets |
| PolyFun-SuSiE | Functionally informed fine-mapping | generated externally | credible sets |
| [FinnGen fine-mapping pipeline](https://github.com/FINNGEN/finemapping-pipeline) | Reference pipeline and output conventions | code and documentation | credible sets |
| Gentropy / genetics resources | Precomputed post-GWAS outputs where available | generated externally or downloaded | credible sets |

Expected columns:

```text
locus_id, SNP, CHR, BP, PIP, credible_set, method
```

PIP is posterior inclusion probability. Credible sets are not proof of
causality; they depend on LD quality, ancestry matching and model assumptions.

## 4. QTL And Colocalisation

| Resource or tool | Purpose | Access mode | DrugPipe table |
| --- | --- | --- | --- |
| [eQTL Catalogue](https://www.ebi.ac.uk/eqtl/Data_access/) | eQTL/sQTL summary statistics and metadata | FTP, API and browser | coloc summary after external analysis |
| [GTEx](https://gtexportal.org/) | Tissue QTL resources | portal and downloads | coloc summary after external analysis |
| genetics resources with QTL outputs | Precomputed QTL and coloc evidence | downloads or generated externally | coloc summary |
| coloc / SuSiE-coloc | Shared-signal analysis | generated externally | coloc summary |

Expected columns:

```text
locus_id, gene_name, qtl_type, tissue_or_cell, pp_h4, pp_h3, effect_direction
```

PP_H4 supports a shared causal signal. Tissue relevance, ancestry, LD and QTL
sample size strongly affect interpretation.

## 5. Expression And Cell Context

| Resource | Purpose | Access mode | DrugPipe table |
| --- | --- | --- | --- |
| [Human Protein Atlas](https://www.proteinatlas.org/about/download) | Protein class and expression summaries | direct downloads | marker or annotation tables |
| [Human Cell Atlas](https://www.humancellatlas.org/) | Single-cell reference data | portal and downloads | processed expression summaries |
| [HuBMAP](https://hubmapconsortium.org/) | Tissue maps and molecular data | portal and API | processed expression summaries |
| GEO / ArrayExpress bone datasets | Public bone-cell expression studies | study downloads | processed expression summaries |

Common inputs:

```text
expression matrix
sample metadata
cell marker table: gene_name, cell_type, marker_strength
```

DrugPipe currently scores marker tables; raw expression preprocessing should be
done upstream.

## 6. Pathways

| Resource | Purpose | Access mode | DrugPipe table |
| --- | --- | --- | --- |
| [Reactome](https://reactome.org/download-data) | Curated pathways and gene sets | direct downloads and web tools | pathway gene sets |
| Gene Ontology | Functional annotations | direct downloads | pathway gene sets |
| MSigDB | Gene sets for enrichment | licence-controlled downloads | pathway gene sets |
| KEGG | Pathway annotations | licence-dependent | pathway gene sets |

Expected columns:

```text
pathway_name, gene_name
```

Pathway results are useful for mechanism interpretation but can be redundant
and annotation-biased.

## 7. MR And Safety

| Resource or tool | Purpose | Access mode | DrugPipe table |
| --- | --- | --- | --- |
| OpenGWAS | Exposure/outcome GWAS sources | API and web interface | MR summaries |
| TwoSampleMR | MR workflow tooling | generated externally | MR summaries |
| FinnGen endpoints | Phenome-wide outcomes where available | portal and downloads | Phe-MR summaries |
| Published druggable-genome MR studies | Target validation evidence | literature and supplementary tables | MR summaries |

Expected MR columns:

```text
gene_name, exposure_type, exposure_id, outcome, beta, se, p, f_statistic, method, direction
```

DrugPipe imports MR summaries. It does not prove causality; instrument validity,
pleiotropy and directionality checks remain essential.

## 8. Druggability And Target Annotation

| Resource | Purpose | Access mode | DrugPipe table |
| --- | --- | --- | --- |
| Open Targets Platform | Target-disease, tractability and safety evidence | portal, API and downloads | target annotation |
| [ChEMBL](https://www.ebi.ac.uk/chembl/) | Bioactivity and known drug information | downloads and API | target annotation |
| [Pharos](https://pharos.nih.gov/) | Target development level and annotations | portal and API | target annotation |
| Human Protein Atlas protein classes | Protein class and tissue expression context | downloads | target annotation |

Expected columns:

```text
gene_name, target_class, tractability_modality, tractability_score, known_drug, known_drug_name, safety_note
```

Druggability supports prioritisation but does not guarantee therapeutic
feasibility.

## 9. Plotting Inputs

Standard figure recipes consume small analysis tables:

```text
PCA scores: sample_id, PC1, PC2, group, batch
expression matrix: genes x samples
metadata: sample_id, group, batch
differential expression: gene_name, log2_fold_change, adjusted_p_value
GWAS table: SNP, CHR, BP, P
enrichment results: pathway_name, adjusted_p_value, n_genes
MR/effect table: exposure, outcome, beta, se, p
target score table: gene_name and evidence score columns
```
