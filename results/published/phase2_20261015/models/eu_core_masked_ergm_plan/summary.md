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
| M0 | log_loss | 3 | 0.9363 | 0.0000 |
| M0 | pr_auc | 3 | 0.5000 | 0.0000 |
| M0 | recall | 3 | 0.0000 | 0.0000 |
| M0 | roc_auc | 3 | 0.5000 | 0.0000 |
| M1 | accuracy | 3 | 0.7886 | 0.0113 |
| M1 | f1 | 3 | 0.7436 | 0.0166 |
| M1 | log_loss | 3 | 0.6783 | 0.0194 |
| M1 | matthews_correlation | 3 | 0.6161 | 0.0200 |
| M1 | pr_auc | 3 | 0.7724 | 0.0124 |
| M1 | precision | 3 | 0.9438 | 0.0068 |
| M1 | recall | 3 | 0.6136 | 0.0202 |
| M1 | roc_auc | 3 | 0.7886 | 0.0113 |
| M3 | accuracy | 3 | 0.7796 | 0.0153 |
| M3 | f1 | 3 | 0.7293 | 0.0232 |
| M3 | log_loss | 3 | 0.6434 | 0.0211 |
| M3 | matthews_correlation | 3 | 0.6021 | 0.0263 |
| M3 | pr_auc | 3 | 0.8752 | 0.0104 |
| M3 | precision | 3 | 0.9439 | 0.0075 |
| M3 | recall | 3 | 0.5945 | 0.0285 |
| M3 | roc_auc | 3 | 0.8798 | 0.0115 |
| M4c | accuracy | 3 | 0.7214 | 0.0016 |
| M4c | f1 | 3 | 0.6275 | 0.0043 |
| M4c | log_loss | 3 | 0.5817 | 0.0185 |
| M4c | matthews_correlation | 3 | 0.5127 | 0.0009 |
| M4c | pr_auc | 3 | 0.9083 | 0.0075 |
| M4c | precision | 3 | 0.9465 | 0.0043 |
| M4c | recall | 3 | 0.4693 | 0.0059 |
| M4c | roc_auc | 3 | 0.9174 | 0.0068 |

## Metric statuses requiring inspection

- `M0` / `matthews_correlation`: `not_defined_single_predicted_class` in 3 replicate(s).
- `M0` / `precision`: `not_defined_no_predicted_positive` in 3 replicate(s).

Inspect `model_status.csv` for any fit or prediction failure and `metrics.csv` for replicate-level values before interpreting score differences.
