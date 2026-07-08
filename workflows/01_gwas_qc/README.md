# GWAS QC And Locus Definition

## Scientific Question

Which variants pass basic GWAS summary-statistic checks, and which
genome-wide-significant regions should be followed up as loci?

## When To Use This Step

Use this at the start of a post-GWAS study after obtaining summary statistics.
It produces harmonised variants and a locus table for downstream gene mapping,
fine-mapping import and evidence integration.

## Typical Inputs

- GWAS summary statistics
- genome build and ancestry metadata
- QC thresholds for INFO, MAF and ambiguous SNP handling

## Recommended Established Tools

- LDSC `munge_sumstats`
- PLINK where genotype-level checks are appropriate
- cohort-specific GWAS QC scripts

## Public Data Resources

- [GWAS Catalog](https://www.ebi.ac.uk/gwas/downloads) - direct downloads and study pages
- [GEFOS](http://www.gefos.org/) - bone-focused GWAS resources
- [OpenGWAS](https://gwas.mrcieu.ac.uk/) - API and web interface

## Example Workflow

1. Confirm phenotype, genome build, ancestry and sample size.
2. Harmonise column names.
3. Filter low INFO, low MAF, missing effects and ambiguous alleles.
4. Identify variants passing the genome-wide threshold.
5. Merge overlapping lead-SNP windows into loci.
6. Export `harmonised_sumstats.tsv.gz` and `loci.tsv`.

## DrugPipe Example

```bash
osteo-target-gwas qc --gwas data/example/example_gwas.tsv --outdir results/example
osteo-target-gwas define-loci --gwas results/example/qc/harmonised_sumstats.tsv.gz --outdir results/example
```

## Expected Output Schema

`results/example/loci/loci.tsv` includes:

```text
locus_id, CHR, START, END, LEAD_SNP, LEAD_BP, LEAD_P, LEAD_BETA, LEAD_SE,
N_VARIANTS, N_SIGNIFICANT_VARIANTS
```

## Interpretation

`LEAD_P` identifies the strongest association in the locus. Locus windows are
analysis conveniences, not proof of causal boundaries.

## Caveats

Genome build mismatches, ancestry differences, allele flips and sample overlap
can all affect downstream interpretation.
