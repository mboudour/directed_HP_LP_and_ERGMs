# Masked ERGM conditional-score summary

This is a score-discrimination summary for exact conditional ERGM probabilities fitted to masked training networks. It is not an inferential ERGM table and not a forecasting result.

## Completion status

- Replicates: 3 (completed=3)
- Model-replicate outcomes: 18 (scored=18)

## Discrimination metrics across completed replicates

| Model | Metric | Completed replicates | Mean | SD |
|---|---|---:|---:|---:|
| M0 | accuracy | 3 | 0.5000 | 0.0000 |
| M0 | f1 | 3 | 0.0000 | 0.0000 |
| M0 | log_loss | 3 | 0.7338 | 0.0000 |
| M0 | pr_auc | 3 | 0.5000 | 0.0000 |
| M0 | recall | 3 | 0.0000 | 0.0000 |
| M0 | roc_auc | 3 | 0.5000 | 0.0000 |
| M1 | accuracy | 3 | 0.5000 | 0.0000 |
| M1 | f1 | 3 | 0.0000 | 0.0000 |
| M1 | log_loss | 3 | 0.6974 | 0.0011 |
| M1 | pr_auc | 3 | 0.5953 | 0.0025 |
| M1 | recall | 3 | 0.0000 | 0.0000 |
| M1 | roc_auc | 3 | 0.6377 | 0.0028 |
| M2 | accuracy | 3 | 0.5000 | 0.0000 |
| M2 | f1 | 3 | 0.0000 | 0.0000 |
| M2 | log_loss | 3 | 0.6608 | 0.0024 |
| M2 | pr_auc | 3 | 0.7278 | 0.0021 |
| M2 | recall | 3 | 0.0000 | 0.0000 |
| M2 | roc_auc | 3 | 0.7576 | 0.0037 |
| M3 | accuracy | 3 | 0.5001 | 0.0024 |
| M3 | f1 | 3 | 0.0086 | 0.0030 |
| M3 | log_loss | 3 | 0.6607 | 0.0026 |
| M3 | matthews_correlation | 3 | 0.0046 | 0.0350 |
| M3 | pr_auc | 3 | 0.6256 | 0.0228 |
| M3 | precision | 3 | 0.5591 | 0.2564 |
| M3 | recall | 3 | 0.0044 | 0.0015 |
| M3 | roc_auc | 3 | 0.6755 | 0.0148 |
| M4 | accuracy | 3 | 0.5021 | 0.0037 |
| M4 | f1 | 3 | 0.0292 | 0.0173 |
| M4 | log_loss | 3 | 0.6600 | 0.0025 |
| M4 | matthews_correlation | 3 | 0.0136 | 0.0343 |
| M4 | pr_auc | 3 | 0.6518 | 0.0184 |
| M4 | precision | 3 | 0.5354 | 0.1644 |
| M4 | recall | 3 | 0.0150 | 0.0090 |
| M4 | roc_auc | 3 | 0.6950 | 0.0118 |
| M4c | accuracy | 3 | 0.5822 | 0.0068 |
| M4c | f1 | 3 | 0.3805 | 0.0170 |
| M4c | log_loss | 3 | 0.6423 | 0.0021 |
| M4c | matthews_correlation | 3 | 0.2165 | 0.0148 |
| M4c | pr_auc | 3 | 0.6884 | 0.0052 |
| M4c | precision | 3 | 0.7353 | 0.0124 |
| M4c | recall | 3 | 0.2568 | 0.0146 |
| M4c | roc_auc | 3 | 0.7347 | 0.0026 |

## Metric statuses requiring inspection

- `M0` / `matthews_correlation`: `not_defined_single_predicted_class` in 3 replicate(s).
- `M0` / `precision`: `not_defined_no_predicted_positive` in 3 replicate(s).
- `M1` / `matthews_correlation`: `not_defined_single_predicted_class` in 3 replicate(s).
- `M1` / `precision`: `not_defined_no_predicted_positive` in 3 replicate(s).
- `M2` / `matthews_correlation`: `not_defined_single_predicted_class` in 3 replicate(s).
- `M2` / `precision`: `not_defined_no_predicted_positive` in 3 replicate(s).

Inspect `model_status.csv` for any fit or prediction failure and `metrics.csv` for replicate-level values before interpreting score differences.
