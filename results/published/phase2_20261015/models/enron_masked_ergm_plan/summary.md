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
| M0 | log_loss | 3 | 1.5741 | 0.0000 |
| M0 | pr_auc | 3 | 0.5000 | 0.0000 |
| M0 | recall | 3 | 0.0000 | 0.0000 |
| M0 | roc_auc | 3 | 0.5000 | 0.0000 |
| M1 | accuracy | 3 | 0.5000 | 0.0000 |
| M1 | f1 | 3 | 0.0000 | 0.0000 |
| M1 | log_loss | 3 | 1.1741 | 0.0474 |
| M1 | pr_auc | 3 | 0.7184 | 0.0178 |
| M1 | recall | 3 | 0.0000 | 0.0000 |
| M1 | roc_auc | 3 | 0.7263 | 0.0160 |
| M3 | accuracy | 3 | 0.6325 | 0.0154 |
| M3 | f1 | 3 | 0.4216 | 0.0346 |
| M3 | log_loss | 3 | 0.9623 | 0.0338 |
| M3 | matthews_correlation | 3 | 0.3861 | 0.0314 |
| M3 | pr_auc | 3 | 0.9242 | 0.0099 |
| M3 | precision | 3 | 0.9867 | 0.0231 |
| M3 | recall | 3 | 0.2684 | 0.0273 |
| M3 | roc_auc | 3 | 0.9190 | 0.0061 |
| M4c | accuracy | 3 | 0.6281 | 0.0092 |
| M4c | f1 | 3 | 0.4110 | 0.0182 |
| M4c | log_loss | 3 | 0.9636 | 0.0290 |
| M4c | matthews_correlation | 3 | 0.3788 | 0.0230 |
| M4c | pr_auc | 3 | 0.9243 | 0.0090 |
| M4c | precision | 3 | 0.9864 | 0.0236 |
| M4c | recall | 3 | 0.2596 | 0.0132 |
| M4c | roc_auc | 3 | 0.9186 | 0.0037 |

## Metric statuses requiring inspection

- `M0` / `matthews_correlation`: `not_defined_single_predicted_class` in 3 replicate(s).
- `M0` / `precision`: `not_defined_no_predicted_positive` in 3 replicate(s).
- `M1` / `matthews_correlation`: `not_defined_single_predicted_class` in 3 replicate(s).
- `M1` / `precision`: `not_defined_no_predicted_positive` in 3 replicate(s).

Inspect `model_status.csv` for any fit or prediction failure and `metrics.csv` for replicate-level values before interpreting score differences.
