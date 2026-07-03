# DrugPipe

DrugPipe is a Python package scaffold for a reproducible osteoporosis
post-GWAS target-discovery pipeline.

The intended workflow starts from osteoporosis, bone mineral density, and
fracture GWAS summary statistics, then builds evidence for candidate targets
through quality control, locus definition, fine-mapping-ready credible sets,
variant-to-gene mapping, QTL colocalisation, bone-cell context, pathway
interpretation, Mendelian randomisation, druggability annotation, target
scoring, and target evidence cards.

## CLI

The command-line interface is built with Typer:

```bash
osteo-target-gwas --help
```

The current commands are placeholders and will report that they exist but are
not implemented yet.
