# Workflow Examples

These shell scripts show a staged DrugPipe analysis pattern. They are examples,
not a workflow engine. Real projects should run upstream heavy analyses with
their chosen tools, then import summary-level outputs into DrugPipe.

Recommended order:

```text
01_gwas_qc_and_loci.sh
02_gene_mapping_and_finemap_import.sh
03_qtl_and_omics_evidence.sh
04_mr_safety_druggability.sh
05_target_scoring_and_reports.sh
06_standard_figures.sh
```

For the synthetic demo, `make example` runs the whole local-file workflow.
