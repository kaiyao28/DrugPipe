# QTL Colocalisation

## Scientific Question

Does the GWAS association and molecular QTL signal appear consistent with a
shared causal variant?

## When To Use This Step

Use this after loci and candidate genes are available. Colocalisation links
genetic associations to molecular traits in relevant tissues or cells.

## Typical Inputs

- GWAS summary statistics by locus
- QTL summary statistics
- tissue or cell metadata
- external colocalisation summaries

## Recommended Established Tools

- coloc
- SuSiE-coloc
- SMR/HEIDI as a related prioritisation method

## Public Data Resources

- [eQTL Catalogue](https://www.ebi.ac.uk/eqtl/Data_access/) - FTP, API and browser
- [GTEx](https://gtexportal.org/) - portal and downloads
- Open Targets Genetics - browser/platform and downloadable outputs where available

## Example Workflow

1. Harmonise GWAS and QTL variants.
2. Restrict analysis to a locus.
3. Check allele orientation.
4. Run coloc or SuSiE-coloc externally.
5. Inspect PP_H3 and PP_H4.
6. Export a gene-level summary table.

## DrugPipe Example

```bash
osteo-target-gwas coloc --coloc data/example/coloc_results.tsv --outdir results/example
```

## Expected Output Schema

```text
locus_id, gene_name, qtl_type, tissue_or_cell, pp_h4, pp_h3, effect_direction
```

## Interpretation

High PP_H4 supports a shared signal. PP_H3 suggests distinct causal signals in
the region. Tissue relevance and direction of effect matter.

## Caveats

LD quality, ancestry mismatch, sample overlap, tissue relevance and multiple
causal signals can change conclusions.
