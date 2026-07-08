# Minimal coloc-style pseudocode.
# Replace inputs with harmonised locus-level GWAS and QTL tables.

# library(coloc)
#
# result <- coloc.abf(
#   dataset1 = list(beta = gwas$beta, varbeta = gwas$se^2, snp = gwas$snp, type = "quant"),
#   dataset2 = list(beta = qtl$beta, varbeta = qtl$se^2, snp = qtl$snp, type = "quant")
# )
#
# write.table(result$summary, "coloc_summary.tsv", sep = "\t", quote = FALSE)
