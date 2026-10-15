# Paired frozen-mask uncertainty analysis

- Dataset: `enron_20150507`
- Source family: `native_heuristic`
- Fixed reference: `lifted_adamic_adar_total_mean`
- Resampling unit: the whole frozen mask replicate.
- Interval: 95% percentile bootstrap (10,000 replications).
- Test: two-sided paired sign-flip permutation (20,000 replications).
- Scope: within-dataset comparisons only; mask replicates are never treated as independent networks across datasets.

See `paired_differences.csv` for all predeclared reference contrasts.
