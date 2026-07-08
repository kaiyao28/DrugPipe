#!/usr/bin/env bash
set -euo pipefail

OUTDIR=${OUTDIR:-results/example}
CONFIG=${CONFIG:-config/default.yaml}
REPORT=${REPORT:-reports/example/target_prioritisation_report.md}
CARDS_DIR=${CARDS_DIR:-reports/example/target_cards}

osteo-target-gwas score-targets \
  --results "$OUTDIR" \
  --config "$CONFIG"

osteo-target-gwas report \
  --results "$OUTDIR" \
  --out "$REPORT"

osteo-target-gwas make-target-cards \
  --results "$OUTDIR" \
  --top-n 10 \
  --outdir "$CARDS_DIR"
