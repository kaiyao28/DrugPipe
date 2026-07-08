# Pathway And Enrichment Analysis

## Scientific Question

Which biological mechanisms are represented among candidate or prioritised
genes?

## When To Use This Step

Use this after locus-to-gene mapping and before final interpretation. It helps
organise target hypotheses into mechanisms.

## Typical Inputs

- candidate gene list
- pathway-to-gene table
- optional enrichment results from external tools

## Recommended Established Tools

- Reactome analysis tools
- g:Profiler
- clusterProfiler
- Enrichr
- local ORA/GSEA scripts

## Public Data Resources

- [Reactome](https://reactome.org/download-data)
- Gene Ontology
- MSigDB
- g:Profiler

## Example Workflow

1. Select candidate or ranked genes.
2. Map genes to pathway gene sets.
3. Run ORA/GSEA externally where needed.
4. Import pathway context into DrugPipe.

## DrugPipe Example

```bash
osteo-target-gwas pathway \
  --gene-map results/example/genes/locus_gene_map.tsv \
  --gene-sets data/example/pathway_gene_sets.tsv \
  --outdir results/example
```

## Expected Output Schema

```text
pathway_name, gene_name
```

## Interpretation

Pathways help describe mechanism. They should be interpreted alongside genetic
and molecular evidence.

## Caveats

Pathway databases are redundant, incomplete and annotation-biased.
