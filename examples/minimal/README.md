# Minimal Example

The minimum DrugPipe run requires:

```text
--gwas
--genes
--config
--outdir
```

Optional evidence layers are skipped with warnings. A minimal real analysis can
therefore start with harmonised GWAS summary statistics and a matching gene
annotation file, then add fine-mapping, QTL, MR and druggability evidence later.
