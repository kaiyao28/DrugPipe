#!/usr/bin/env bash
set -euo pipefail

OUTDIR=${OUTDIR:-results/example}
GENES=${GENES:-data/example/gene_annotation.tsv}
L2G=${L2G:-data/example/l2g_scores.tsv}
CREDIBLE_SETS=${CREDIBLE_SETS:-data/example/credible_sets.tsv}

osteo-target-gwas finemap \
  --gwas "$OUTDIR/qc/harmonised_sumstats.tsv.gz" \
  --loci "$OUTDIR/loci/loci.tsv" \
  --credible-sets "$CREDIBLE_SETS" \
  --outdir "$OUTDIR"

osteo-target-gwas map-genes \
  --loci "$OUTDIR/loci/loci.tsv" \
  --genes "$GENES" \
  --l2g "$L2G" \
  --outdir "$OUTDIR"
