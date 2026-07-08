# Analysis Modules

DrugPipe is organised around analysis themes rather than one mandatory
end-to-end process. Each module documents the scientific question, common
external tools, public resources, expected DrugPipe summary table and
interpretation cautions.

| Goal | Module |
| --- | --- |
| GWAS QC and loci | [01_gwas_qc](01_gwas_qc/README.md) |
| map loci to genes | [02_locus_to_gene](02_locus_to_gene/README.md) |
| interpret fine-mapping | [03_finemapping](03_finemapping/README.md) |
| integrate QTL evidence | [04_qtl_colocalisation](04_qtl_colocalisation/README.md) |
| analyse expression/cell context | [05_expression_cell_context](05_expression_cell_context/README.md) |
| pathway analysis | [06_pathway_enrichment](06_pathway_enrichment/README.md) |
| MR target validation | [07_mr_target_validation](07_mr_target_validation/README.md) |
| safety/druggability | [08_safety_druggability](08_safety_druggability/README.md) |
| integrate target evidence | [09_target_integration](09_target_integration/README.md) |
| make standard figures | [10_standard_figures](10_standard_figures/README.md) |

For the toy integration demo, run:

```bash
make demo
```
