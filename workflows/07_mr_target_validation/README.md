# Mendelian Randomisation And Target Validation

## Scientific Question

Does genetically proxied perturbation of a target or exposure support an effect
on disease-relevant outcomes?

## When To Use This Step

Use this after candidate genes and exposures have been defined. DrugPipe imports
MR summaries from external workflows.

## Typical Inputs

- exposure GWAS or molecular instrument table
- outcome GWAS
- instrument strength metrics
- MR summary results

## Recommended Established Tools

- TwoSampleMR
- MendelianRandomization
- OpenGWAS-based workflows

## Public Data Resources

- [OpenGWAS](https://gwas.mrcieu.ac.uk/)
- public GWAS summary statistics
- FinnGen endpoints where available

## Example Workflow

1. Define instruments.
2. Harmonise exposure and outcome alleles.
3. Run MR externally.
4. Check instrument strength and sensitivity analyses.
5. Export gene-level MR summaries.

## DrugPipe Example

```bash
osteo-target-gwas mr-targets --mr data/example/mr_results.tsv --outdir results/example
```

## Expected Output Schema

```text
gene_name, exposure_type, exposure_id, outcome, beta, se, p, f_statistic, method, direction
```

## Interpretation

Direction, effect size, p-value and F-statistic help assess support. MR does not
prove therapeutic causality without instrument validity and pleiotropy checks.

## Caveats

Weak instruments, horizontal pleiotropy, sample overlap and phenotype mismatch
can bias results.
