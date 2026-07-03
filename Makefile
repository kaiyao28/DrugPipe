.PHONY: install test example clean

install:
	python -m pip install --upgrade pip
	python -m pip install -e .
	python -m pip install pytest

test:
	python -m pytest

example:
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

clean:
	rm -rf results/example reports/example
