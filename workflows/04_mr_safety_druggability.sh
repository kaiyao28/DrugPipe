#!/usr/bin/env bash
set -euo pipefail

OUTDIR=${OUTDIR:-results/example}
MR=${MR:-data/example/mr_results.tsv}
MEDIATION=${MEDIATION:-data/example/mediation_mr_results.tsv}
PHE_MR=${PHE_MR:-data/example/phe_mr_results.tsv}
DRUGGABILITY=${DRUGGABILITY:-data/example/druggability.tsv}

osteo-target-gwas mr-targets \
  --mr "$MR" \
  --outdir "$OUTDIR"

osteo-target-gwas mediation-mr \
  --mediation "$MEDIATION" \
  --outdir "$OUTDIR"

osteo-target-gwas phe-mr \
  --phe-mr "$PHE_MR" \
  --outdir "$OUTDIR"

osteo-target-gwas druggability \
  --druggability "$DRUGGABILITY" \
  --outdir "$OUTDIR"
