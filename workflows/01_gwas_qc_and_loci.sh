#!/usr/bin/env bash
set -euo pipefail

GWAS=${GWAS:-data/example/example_gwas.tsv}
CONFIG=${CONFIG:-config/default.yaml}
OUTDIR=${OUTDIR:-results/example}

osteo-target-gwas validate \
  --gwas "$GWAS" \
  --config "$CONFIG" \
  --outdir "$OUTDIR"

osteo-target-gwas qc \
  --gwas "$GWAS" \
  --config "$CONFIG" \
  --outdir "$OUTDIR"

osteo-target-gwas define-loci \
  --gwas "$OUTDIR/qc/harmonised_sumstats.tsv.gz" \
  --config "$CONFIG" \
  --outdir "$OUTDIR"
