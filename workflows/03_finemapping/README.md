# Fine-Mapping

## Scientific Question

Which variants within an associated locus are most plausible causal candidates
under a fine-mapping model?

## When To Use This Step

Use this after GWAS locus definition. DrugPipe imports precomputed credible-set
tables rather than running heavy fine-mapping internally.

## Typical Inputs

- GWAS summary statistics
- locus definitions
- ancestry-matched LD
- precomputed credible sets and PIP values

## Recommended Established Tools

- SuSiE
- FINEMAP
- PolyFun-SuSiE
- [FinnGen fine-mapping pipeline](https://github.com/FINNGEN/finemapping-pipeline)

## Public Data Resources

- GWAS summary statistics from the study of interest
- ancestry-matched LD reference panels
- precomputed fine-mapping outputs where available

## Example Workflow

1. Define loci from GWAS.
2. Prepare ancestry-matched LD externally.
3. Run SuSiE, FINEMAP or another fine-mapping method externally.
4. Inspect credible-set quality and PIP distribution.
5. Export a compact credible-set table for DrugPipe.

## DrugPipe Example

```bash
osteo-target-gwas finemap \
  --gwas results/example/qc/harmonised_sumstats.tsv.gz \
  --loci results/example/loci/loci.tsv \
  --credible-sets data/example/credible_sets.tsv \
  --outdir results/example
```

## Expected Output Schema

```text
locus_id, SNP, CHR, BP, PIP, credible_set, method
```

## Interpretation

PIP is posterior inclusion probability. Credible sets summarise uncertainty;
they are not proof of causality.

## Caveats

Fine-mapping depends on LD, ancestry, sample size, variant coverage and model
assumptions.
