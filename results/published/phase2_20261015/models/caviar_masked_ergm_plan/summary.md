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
| M0 | log_loss | 3 | 2.0383 | 0.0000 |
| M0 | pr_auc | 3 | 0.5000 | 0.0000 |
| M0 | recall | 3 | 0.0000 | 0.0000 |
| M0 | roc_auc | 3 | 0.5000 | 0.0000 |
| M1 | accuracy | 3 | 0.5000 | 0.0000 |
| M1 | f1 | 3 | 0.0000 | 0.0000 |
| M1 | log_loss | 3 | 1.4584 | 0.0229 |
| M1 | pr_auc | 3 | 0.7164 | 0.0146 |
| M1 | recall | 3 | 0.0000 | 0.0000 |
| M1 | roc_auc | 3 | 0.7216 | 0.0098 |
| M3 | accuracy | 3 | 0.5985 | 0.0174 |
| M3 | f1 | 3 | 0.3328 | 0.0414 |
| M3 | log_loss | 3 | 1.3645 | 0.0060 |
| M3 | matthews_correlation | 3 | 0.3241 | 0.0423 |
| M3 | pr_auc | 3 | 0.8770 | 0.0126 |
| M3 | precision | 3 | 0.9792 | 0.0361 |
| M3 | recall | 3 | 0.2008 | 0.0286 |
| M3 | roc_auc | 3 | 0.8590 | 0.0047 |
| M4c | accuracy | 3 | 0.5871 | 0.0183 |
| M4c | f1 | 3 | 0.3005 | 0.0473 |
| M4c | log_loss | 3 | 1.3835 | 0.0225 |
| M4c | matthews_correlation | 3 | 0.3021 | 0.0423 |
| M4c | pr_auc | 3 | 0.8828 | 0.0112 |
| M4c | precision | 3 | 0.9778 | 0.0385 |
| M4c | recall | 3 | 0.1780 | 0.0328 |
| M4c | roc_auc | 3 | 0.8639 | 0.0098 |

## Metric statuses requiring inspection

- `M0` / `matthews_correlation`: `not_defined_single_predicted_class` in 3 replicate(s).
- `M0` / `precision`: `not_defined_no_predicted_positive` in 3 replicate(s).
- `M1` / `matthews_correlation`: `not_defined_single_predicted_class` in 3 replicate(s).
- `M1` / `precision`: `not_defined_no_predicted_positive` in 3 replicate(s).

Inspect `model_status.csv` for any fit or prediction failure and `metrics.csv` for replicate-level values before interpreting score differences.
