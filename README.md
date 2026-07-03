# DrugPipe

DrugPipe is a Python package for a reproducible osteoporosis post-GWAS
target-discovery workflow. It starts from osteoporosis, bone mineral density, or
fracture GWAS summary statistics and builds prioritised target evidence using
QC, locus definition, fine-mapping-ready credible sets, variant-to-gene mapping,
QTL colocalisation, bone-cell context, pathway interpretation, Mendelian
randomisation, safety scanning, druggability annotation, target scoring, reports,
and target evidence cards.

The current implementation is designed around local files and precomputed
evidence tables. It does not yet run real fine-mapping, colocalisation, or
Mendelian randomisation engines; those stages parse validated precomputed
results.

## Installation

```bash
pip install -e .
```

## CLI

```bash
osteo-target-gwas --help
```

Implemented commands:

- `validate`
- `qc`
- `define-loci`
- `finemap`
- `map-genes`
- `coloc`
- `bone-context`
- `pathway`
- `mr-targets`
- `mediation-mr`
- `phe-mr`
- `druggability`
- `score-targets`
- `report`
- `make-target-cards`
- `run`

## Example Data

Synthetic example inputs are provided under `data/example/`. These are not
individual-level data.

Key example files include:

- `example_gwas.tsv`
- `gene_annotation.tsv`
- `credible_sets.tsv`
- `coloc_results.tsv`
- `bone_cell_markers.tsv`
- `pathway_gene_sets.tsv`
- `mr_results.tsv`
- `mediation_mr_results.tsv`
- `phe_mr_results.tsv`
- `druggability.tsv`

## End-To-End Run

```bash
osteo-target-gwas run \
  --gwas data/example/example_gwas.tsv \
  --genes data/example/gene_annotation.tsv \
  --l2g data/example/l2g_scores.tsv \
  --credible-sets data/example/credible_sets.tsv \
  --coloc data/example/coloc_results.tsv \
  --bone-markers data/example/bone_cell_markers.tsv \
  --pathways data/example/pathway_gene_sets.tsv \
  --mr data/example/mr_results.tsv \
  --mediation data/example/mediation_mr_results.tsv \
  --phe-mr data/example/phe_mr_results.tsv \
  --druggability data/example/druggability.tsv \
  --config config/default.yaml \
  --outdir results/example \
  --report reports/example/target_prioritisation_report.md \
  --cards-dir reports/example/target_cards
```

Required inputs for `run` are `--gwas`, `--genes`, `--config`, and `--outdir`.
Optional evidence inputs are skipped with warnings if absent.

The run command executes:

1. `validate`
2. `qc`
3. `define-loci`
4. `finemap`
5. `map-genes`
6. `coloc`
7. `bone-context`
8. `pathway`
9. `mr-targets`
10. `mediation-mr`
11. `phe-mr`
12. `druggability`
13. `score-targets`
14. `report`
15. `make-target-cards`

It writes `results/example/run_manifest.json` with command metadata, inputs,
outputs, completed stages, and skipped stages.

## Main Outputs

Pipeline outputs are written under the selected results directory:

```text
results/example/
  qc/
    schema_validation.json
    harmonised_sumstats.tsv.gz
    qc_summary.json
    qc_report.md
  loci/
    loci.tsv
  finemap/
    credible_sets.tsv
    locus_finemap_summary.tsv
  genes/
    locus_gene_map.tsv
  qtl/
    coloc_results.tsv
    gene_coloc_summary.tsv
  cell_context/
    bone_cell_relevance.tsv
  biology/
    gene_pathway_context.tsv
    pathway_summary.tsv
  mr/
    target_mr_results.tsv
    gene_mr_summary.tsv
    mediation_mr_results.tsv
    gene_mediation_summary.tsv
    phe_mr_results.tsv
    gene_phe_mr_safety_summary.tsv
  targets/
    druggability.tsv
    ranked_targets.tsv
  run_manifest.json
```

Report outputs are written wherever requested:

```text
reports/example/
  target_prioritisation_report.md
  target_cards/
    <GENE_NAME>.md
```

## Individual Commands

Validate and QC GWAS summary statistics:

```bash
osteo-target-gwas validate \
  --gwas data/example/example_gwas.tsv \
  --config config/default.yaml

osteo-target-gwas qc \
  --gwas data/example/example_gwas.tsv \
  --outdir results/example \
  --min-info 0.8 \
  --min-maf 0.01 \
  --remove-ambiguous
```

Define loci and parse fine-mapping-ready credible sets:

```bash
osteo-target-gwas define-loci \
  --gwas results/example/qc/harmonised_sumstats.tsv.gz \
  --outdir results/example \
  --p-threshold 5e-8 \
  --window-kb 500

osteo-target-gwas finemap \
  --gwas results/example/qc/harmonised_sumstats.tsv.gz \
  --loci results/example/loci/loci.tsv \
  --credible-sets data/example/credible_sets.tsv \
  --outdir results/example
```

Map genes and parse evidence layers:

```bash
osteo-target-gwas map-genes \
  --loci results/example/loci/loci.tsv \
  --genes data/example/gene_annotation.tsv \
  --l2g data/example/l2g_scores.tsv \
  --outdir results/example

osteo-target-gwas coloc \
  --coloc data/example/coloc_results.tsv \
  --outdir results/example

osteo-target-gwas bone-context \
  --gene-map results/example/genes/locus_gene_map.tsv \
  --markers data/example/bone_cell_markers.tsv \
  --outdir results/example

osteo-target-gwas pathway \
  --gene-map results/example/genes/locus_gene_map.tsv \
  --gene-sets data/example/pathway_gene_sets.tsv \
  --outdir results/example
```

Parse MR, safety, and druggability evidence:

```bash
osteo-target-gwas mr-targets \
  --mr data/example/mr_results.tsv \
  --outdir results/example

osteo-target-gwas mediation-mr \
  --mediation data/example/mediation_mr_results.tsv \
  --outdir results/example

osteo-target-gwas phe-mr \
  --phe-mr data/example/phe_mr_results.tsv \
  --outdir results/example

osteo-target-gwas druggability \
  --druggability data/example/druggability.tsv \
  --outdir results/example
```

Score targets and generate narrative outputs:

```bash
osteo-target-gwas score-targets \
  --results results/example \
  --config config/default.yaml

osteo-target-gwas report \
  --results results/example \
  --out reports/example/target_prioritisation_report.md

osteo-target-gwas make-target-cards \
  --results results/example \
  --top-n 10 \
  --outdir reports/example/target_cards
```

## Configuration

Default settings are in `config/default.yaml`, including:

- GWAS column mappings
- QC thresholds
- locus definition settings
- target scoring weights
- safety and annotation-bias penalties

Expected external data resources are documented in `config/data_sources.yaml`.

## Testing

```bash
pytest
```
