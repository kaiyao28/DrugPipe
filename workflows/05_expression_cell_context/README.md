# Expression And Cell-Context Analysis

## Scientific Question

Are candidate genes expressed in relevant cells, tissues or states for the
disease biology?

## When To Use This Step

Use this after candidate genes have been identified. DrugPipe currently imports
marker or cell-context summaries rather than raw expression data.

## Typical Inputs

- processed expression matrix
- sample or cell metadata
- marker table
- candidate gene list

## Recommended Established Tools

- Scanpy
- Seurat
- DESeq2, edgeR or limma for bulk RNA-seq
- standard PCA, clustering and differential-expression workflows

## Public Data Resources

- [GEO](https://www.ncbi.nlm.nih.gov/geo/)
- [BioStudies / ArrayExpress](https://www.ebi.ac.uk/biostudies/arrayexpress)
- [Human Cell Atlas](https://www.humancellatlas.org/)
- [HuBMAP](https://hubmapconsortium.org/)
- [Human Protein Atlas](https://www.proteinatlas.org/about/download)

## Example Workflow

1. Process raw expression data upstream.
2. Annotate groups, batches, tissues or cell types.
3. Summarise markers for candidate genes.
4. Export marker strengths for DrugPipe.

## DrugPipe Example

```bash
osteo-target-gwas bone-context \
  --gene-map results/example/genes/locus_gene_map.tsv \
  --markers data/example/bone_cell_markers.tsv \
  --outdir results/example
```

## Expected Output Schema

```text
gene_name, cell_type, marker_strength
```

## Interpretation

High marker strength indicates relevant expression context. It does not prove
that perturbing the gene will affect disease.

## Caveats

Expression depends on tissue, cell state, preprocessing, batch effects and
annotation quality.
