#!/usr/bin/env bash
set -euo pipefail

OUTDIR=${OUTDIR:-results/example}
COLOC=${COLOC:-data/example/coloc_results.tsv}
MARKERS=${MARKERS:-data/example/bone_cell_markers.tsv}
PATHWAYS=${PATHWAYS:-data/example/pathway_gene_sets.tsv}

osteo-target-gwas coloc \
  --coloc "$COLOC" \
  --outdir "$OUTDIR"

osteo-target-gwas bone-context \
  --gene-map "$OUTDIR/genes/locus_gene_map.tsv" \
  --markers "$MARKERS" \
  --outdir "$OUTDIR"

osteo-target-gwas pathway \
  --gene-map "$OUTDIR/genes/locus_gene_map.tsv" \
  --gene-sets "$PATHWAYS" \
  --outdir "$OUTDIR"
