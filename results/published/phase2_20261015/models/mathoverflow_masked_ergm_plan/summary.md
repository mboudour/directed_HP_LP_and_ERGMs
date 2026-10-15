# Masked ERGM conditional-score summary

This is a score-discrimination summary for exact conditional ERGM probabilities fitted to masked training networks. It is not an inferential ERGM table and not a forecasting result.

## Completion status

- Replicates: 3 (completed=3)
- Model-replicate outcomes: 12 (scored=12)

## Discrimination metrics across completed replicates

| Model | Metric | Completed replicates | Mean | SD |
|---|---|---:|---:|---:|
| M0 | accuracy | 3 | 0.5000 | 0.0000 |
| M0 | f1 | 3 | 0.0000 | 0.0000 |
| M0 | log_loss | 3 | 1.3521 | 0.0000 |
| M0 | pr_auc | 3 | 0.5000 | 0.0000 |
| M0 | recall | 3 | 0.0000 | 0.0000 |
| M0 | roc_auc | 3 | 0.5000 | 0.0000 |
| M1 | accuracy | 3 | 0.5000 | 0.0000 |
| M1 | f1 | 3 | 0.0000 | 0.0000 |
| M1 | log_loss | 3 | 1.3396 | 0.0031 |
| M1 | pr_auc | 3 | 0.5262 | 0.0091 |
| M1 | recall | 3 | 0.0000 | 0.0000 |
| M1 | roc_auc | 3 | 0.5376 | 0.0107 |
| M3 | accuracy | 3 | 0.5049 | 0.0016 |
| M3 | f1 | 3 | 0.0194 | 0.0064 |
| M3 | log_loss | 3 | 1.1678 | 0.0123 |
| M3 | matthews_correlation | 3 | 0.0695 | 0.0119 |
| M3 | pr_auc | 3 | 0.7351 | 0.0072 |
| M3 | precision | 3 | 1.0000 | 0.0000 |
| M3 | recall | 3 | 0.0098 | 0.0033 |
| M3 | roc_auc | 3 | 0.7616 | 0.0040 |
| M4c | accuracy | 3 | 0.5038 | 0.0025 |
| M4c | f1 | 3 | 0.0172 | 0.0074 |
| M4c | log_loss | 3 | 1.1676 | 0.0092 |
| M4c | matthews_correlation | 3 | 0.0539 | 0.0290 |
| M4c | pr_auc | 3 | 0.7417 | 0.0069 |
| M4c | precision | 3 | 0.8889 | 0.1925 |
| M4c | recall | 3 | 0.0087 | 0.0038 |
| M4c | roc_auc | 3 | 0.7656 | 0.0075 |

## Metric statuses requiring inspection

- `M0` / `matthews_correlation`: `not_defined_single_predicted_class` in 3 replicate(s).
- `M0` / `precision`: `not_defined_no_predicted_positive` in 3 replicate(s).
- `M1` / `matthews_correlation`: `not_defined_single_predicted_class` in 3 replicate(s).
- `M1` / `precision`: `not_defined_no_predicted_positive` in 3 replicate(s).

Inspect `model_status.csv` for any fit or prediction failure and `metrics.csv` for replicate-level values before interpreting score differences.
