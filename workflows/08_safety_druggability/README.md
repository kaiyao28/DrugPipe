# Safety And Druggability

## Scientific Question

Does a candidate target have tractability evidence, known modality options or
possible safety liabilities?

## When To Use This Step

Use this before final target scoring and reporting. It adds therapeutic
feasibility and safety context to genetic evidence.

## Typical Inputs

- druggability annotation
- known drug or modality evidence
- phenome-wide safety scan summaries
- target class and safety notes

## Recommended Established Tools

- platform or database lookup for target annotation
- Phe-MR workflows
- manual expert review for liabilities

## Public Data Resources

- Open Targets Platform
- [ChEMBL](https://www.ebi.ac.uk/chembl/)
- [Pharos](https://pharos.nih.gov/)
- [Human Protein Atlas](https://www.proteinatlas.org/about/download)

## Example Workflow

1. Search the target in annotation platforms.
2. Record target class, modality and known drug status.
3. Import Phe-MR safety flags where available.
4. Export DrugPipe-compatible annotation tables.

## DrugPipe Example

```bash
osteo-target-gwas phe-mr --phe-mr data/example/phe_mr_results.tsv --outdir results/example
osteo-target-gwas druggability --druggability data/example/druggability.tsv --outdir results/example
```

## Expected Output Schema

```text
gene_name, target_class, tractability_modality, tractability_score, known_drug, known_drug_name, safety_note
```

## Interpretation

Tractability and known drug evidence can support prioritisation, while safety
flags penalise targets needing caution.

## Caveats

Druggability does not guarantee clinical feasibility. Absence of a safety flag
does not prove safety.
