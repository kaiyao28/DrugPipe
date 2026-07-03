def test_package_imports() -> None:
    import osteo_target_gwas

    assert osteo_target_gwas.__version__


def test_subpackages_import() -> None:
    import osteo_target_gwas.biology
    import osteo_target_gwas.finemap
    import osteo_target_gwas.genes
    import osteo_target_gwas.io
    import osteo_target_gwas.loci
    import osteo_target_gwas.mr
    import osteo_target_gwas.qc
    import osteo_target_gwas.qtl
    import osteo_target_gwas.report
    import osteo_target_gwas.targets
