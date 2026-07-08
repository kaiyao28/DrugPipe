"""Minimal Scanpy-style PCA example for upstream expression preprocessing."""

# import scanpy as sc
#
# adata = sc.read_h5ad("expression.h5ad")
# sc.pp.normalize_total(adata)
# sc.pp.log1p(adata)
# sc.pp.highly_variable_genes(adata)
# sc.tl.pca(adata)
# adata.obs[["group", "batch"]].to_csv("metadata.tsv", sep="\t")
# adata.obsm["X_pca"].tofile("pca_scores.tsv", sep="\t")
