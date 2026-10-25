# Paired frozen-mask uncertainty analysis

- Dataset: `senate_118_s_bills`
- Source family: `native_ergm`
- Fixed reference: `M5::L1g`
- Resampling unit: the whole frozen mask replicate.
- Interval: 95% percentile bootstrap (10,000 replications).
- Test: two-sided paired sign-flip permutation (20,000 replications).
- Scope: within-dataset comparisons only; mask replicates are never treated as independent networks across datasets.

See `paired_differences.csv` for all predeclared reference contrasts.
