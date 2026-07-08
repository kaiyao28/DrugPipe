# External Tools

DrugPipe is the integration and reporting layer. Heavy computations should
remain modular, auditable and reproducible outside or upstream of DrugPipe.

## 1. GWAS QC And Harmonisation

Useful upstream tools include:

- LDSC `munge_sumstats`
- cohort-specific QC scripts
- PLINK where genotype-level filtering is appropriate

DrugPipe can validate and filter summary statistics, but real projects should
document build, ancestry, sample size, allele harmonisation and imputation QC.

## 2. Fine-Mapping

Common external tools:

- SuSiE
- FINEMAP
- PolyFun-SuSiE
- FinnGen fine-mapping pipeline

DrugPipe imports credible-set and PIP tables. It does not need to run full
fine-mapping on large datasets inside the package.

## 3. Colocalisation

Common external tools and resources:

- coloc
- SuSiE-coloc
- eQTL Catalogue region/API workflows
- SMR/HEIDI as a related prioritisation method

DrugPipe imports per-gene summaries such as `pp_h4`, `pp_h3`, QTL type, tissue
or cell context and effect direction.

## 4. Expression Preprocessing

Common upstream tools:

- Scanpy for single-cell analysis in Python
- Seurat for single-cell analysis in R
- DESeq2, edgeR or limma for bulk RNA-seq
- standard PCA, clustering and differential-expression workflows

DrugPipe plotting recipes accept cleaned matrices, metadata and marker tables;
they are not raw FASTQ/BAM processing workflows.

## 5. Mendelian Randomisation

Common external tools:

- TwoSampleMR
- MendelianRandomization
- OpenGWAS-based workflows

DrugPipe imports MR summary tables with beta, standard error, p-value,
instrument strength, method and direction.

## 6. Pathway Analysis

Common external tools:

- Reactome web analysis tools
- g:Profiler
- clusterProfiler
- Enrichr
- local ORA/GSEA scripts

DrugPipe can import pathway-to-gene tables and pathway summaries for target
interpretation.

## 7. Target Annotation

Common annotation platforms:

- Open Targets Platform
- ChEMBL
- Pharos
- Human Protein Atlas

For batch work, reduce downloaded or API-derived annotations to gene-level
fields such as target class, tractability modality, known drug status and
safety note.
