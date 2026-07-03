# DrugPipe

![DrugPipe banner](docs/assets/drugpipe-banner.svg)

[![Tests](https://github.com/kaiyao28/DrugPipe/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/kaiyao28/DrugPipe/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-334155)
![CLI](https://img.shields.io/badge/CLI-osteo--target--gwas-0f766e)
![Status](https://img.shields.io/badge/status-local--file%20MVP-b45309)

DrugPipe is a lightweight local-file pipeline for post-GWAS target prioritisation
in osteoporosis, bone mineral density and fracture-risk studies.

It starts from GWAS summary statistics, combines genetic and biological evidence,
and produces ranked candidate drug targets plus Markdown reports and target
evidence cards.

The Python package and command-line entry point are named `osteo-target-gwas`:

```bash
osteo-target-gwas --help
```

## What DrugPipe Does

GWAS can identify genomic regions associated with osteoporosis or bone mineral
density, but a GWAS hit does not directly identify the causal gene, the relevant
bone cell type, druggability, or possible safety liabilities.

DrugPipe organises these evidence layers into one reproducible workflow:

![DrugPipe workflow](docs/assets/drugpipe-workflow.svg)

The output is a ranked list of target hypotheses for follow-up. It is not proof
that a target is causal, safe, or clinically actionable.

## Current Status

DrugPipe currently works with local input files and precomputed evidence tables.

It can validate and QC GWAS summary statistics, define significant loci, parse
precomputed credible sets, map loci to genes, parse precomputed QTL
colocalisation and Mendelian randomisation evidence, score bone-cell and pathway
context, annotate druggability, rank targets, and generate Markdown reports.

It does not yet run full external fine-mapping, colocalisation, or MR engines
from raw inputs. Those stages currently expect precomputed result tables.

## Installation

```bash
pip install -e .
```

Check the CLI:

```bash
osteo-target-gwas --help
```

Run tests:

```bash
pytest
```

## Run The Example

The example uses small synthetic files in `data/example/`. These are not
individual-level data.

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

Required inputs are `--gwas`, `--genes`, `--config`, and `--outdir`. Optional
evidence files are skipped with warnings when they are not supplied.

## Main Outputs

After a successful run, the main results are:

```text
results/example/
  qc/
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
    gene_coloc_summary.tsv
  cell_context/
    bone_cell_relevance.tsv
  biology/
    gene_pathway_context.tsv
    pathway_summary.tsv
  mr/
    gene_mr_summary.tsv
    gene_mediation_summary.tsv
    gene_phe_mr_safety_summary.tsv
  targets/
    druggability.tsv
    ranked_targets.tsv
  run_manifest.json
```

Report outputs are written to:

```text
reports/example/
  target_prioritisation_report.md
  target_cards/
    <GENE_NAME>.md
```

## Target Scoring

DrugPipe combines evidence from several layers:

```text
target score =
    genetic association evidence
  + fine-mapping evidence
  + locus-to-gene evidence
  + QTL colocalisation evidence
  + bone-cell context
  + pathway context
  + MR target-validation evidence
  + druggability evidence
  - safety penalty
  - annotation-bias penalty
```

The scoring weights are defined in `config/default.yaml`. The score is intended
to rank target hypotheses for follow-up, not to make causal claims.

## Individual Commands

Most users should start with the end-to-end `run` command. The main individual
commands are useful for debugging or rerunning one stage:

```bash
osteo-target-gwas validate \
  --gwas data/example/example_gwas.tsv \
  --config config/default.yaml

osteo-target-gwas qc \
  --gwas data/example/example_gwas.tsv \
  --outdir results/example \
  --config config/default.yaml

osteo-target-gwas define-loci \
  --gwas results/example/qc/harmonised_sumstats.tsv.gz \
  --outdir results/example \
  --config config/default.yaml

osteo-target-gwas map-genes \
  --loci results/example/loci/loci.tsv \
  --genes data/example/gene_annotation.tsv \
  --l2g data/example/l2g_scores.tsv \
  --outdir results/example

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

## Using Real Data

To move beyond the synthetic example, replace the files in `data/example/` with
public or internal summary-level resources that follow the documented schemas.

Typical inputs include:

| Evidence layer | Example input |
| --- | --- |
| GWAS | Osteoporosis, BMD, or fracture GWAS summary statistics |
| Genes | Ensembl or GENCODE gene annotation |
| Fine-mapping | Precomputed credible sets with PIP values |
| QTL evidence | Precomputed eQTL, sQTL, pQTL, caQTL, or other colocalisation results |
| Cell context | Bone-cell marker or expression table |
| Pathways | Reactome, GO, KEGG, or custom bone-remodelling gene sets |
| MR | Precomputed target MR results |
| Mediation MR | Mediator evidence such as BMI, diabetes, immune, or lipid traits |
| Phe-MR | Phenome-wide safety scan results |
| Druggability | Target class, modality, known drug, and safety annotations |

Expected external resources are documented in `config/data_sources.yaml`.

## Caveats

DrugPipe is for research prioritisation only.

A high-ranking target is not automatically causal, safe, or therapeutically
useful. Interpretation depends on the quality of the input evidence.

Key limitations:

- nearest-gene mapping is weak by itself;
- fine-mapping depends on ancestry-matched LD;
- colocalisation depends on tissue relevance and QTL quality;
- MR depends on valid genetic instruments;
- Phe-MR safety scans are incomplete;
- druggability does not guarantee therapeutic feasibility;
- all results require biological and experimental validation.

## Roadmap

Planned improvements:

```text
v0.1  Local-file MVP with example data and reports
v0.2  Better fine-mapping integration
v0.3  Direct colocalisation wrappers
v0.4  Richer bone-cell and single-cell context
v0.5  Additional public target-annotation integrations
v0.6  Workflow-manager wrapper
```
