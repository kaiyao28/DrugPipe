# Locus-To-Gene Mapping

## Scientific Question

Which candidate genes should be considered for each GWAS locus?

## When To Use This Step

Use this after locus definition and before importing molecular or target-level
evidence. The output is the core gene list that later modules annotate.

## Typical Inputs

- locus table
- gene annotation with TSS and gene coordinates
- optional L2G-style scores or regulatory evidence

## Recommended Established Tools

- Ensembl BioMart or GENCODE for annotation
- VEP or other consequence annotation where coding variants are relevant
- external regulatory prioritisation models where available

## Public Data Resources

- [Ensembl BioMart](https://www.ensembl.org/biomart) - direct export/API
- [GENCODE](https://www.gencodegenes.org/) - direct annotation downloads

## Example Workflow

1. Match gene annotation to GWAS genome build.
2. Map genes overlapping each locus.
3. Compute distance from lead SNP to TSS.
4. Import optional L2G scores.
5. Export one row per locus-gene pair.

## DrugPipe Example

```bash
osteo-target-gwas map-genes \
  --loci results/example/loci/loci.tsv \
  --genes data/example/gene_annotation.tsv \
  --l2g data/example/l2g_scores.tsv \
  --outdir results/example
```

## Expected Output Schema

```text
locus_id, gene_id, gene_name, CHR, gene_start, gene_end, tss, nearest_gene,
distance_to_tss, locus_overlap, l2g_score, locus_to_gene_score, evidence_labels
```

## Interpretation

Nearest-gene evidence is useful but weak by itself. Stronger hypotheses combine
distance, overlap, regulatory, molecular and biological support.

## Caveats

Long-range regulation, multiple causal genes and annotation incompleteness can
make locus-to-gene mapping uncertain.
