# Overview

DrugPipe is a modular post-GWAS target-discovery workflow and Python reference
library. It is designed to integrate summary-level evidence after upstream
genetics and omics analyses have been run.

The intended workflow is:

```text
GWAS summary statistics
  -> QC and locus definition
  -> candidate genes
  -> imported evidence layers
  -> ranked targets
  -> reports and target evidence cards
```

DrugPipe intentionally keeps heavy methods external. Fine-mapping,
colocalisation, expression preprocessing and MR can be run with specialised
tools, then imported as compact result tables.

Core documentation:

- [Schemas](schemas.md)
- [Data sources](data_sources.md)
- [External tools](external_tools.md)
- [Interpretation guide](interpretation.md)
- [Plotting recipes](plotting_recipes.md)
