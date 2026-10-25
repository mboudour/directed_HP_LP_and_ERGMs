# ERGM conditional footprint scores for native-event panels

- Dataset: `senate_118_s_bills_cap3_sensitivity_ergm_inputs`
- Each static ERGM is fit separately to a frozen event-first observed projection.
- L1 is the arithmetic mean of conditional-pseudolikelihood dyad scores; L1g is their geometric mean; L2 is their product.
- L2 metrics use `log_L2`, a strictly monotone numeric representation of the L2 product.
- These scores estimate **graph-footprint completion**, not the probability that a recorded email group event occurred.

## Completion status

- Frozen splits: 60 (completed without model failure: 60)
- Inspect `model_status.csv` before interpreting a model or split.

## Ranking metrics across successful replicates

| Panel | Mechanism | Model | Score | Metric | Replicates | Mean | SD |
|---|---|---|---|---|---:|---:|---:|
| random | mcar | M0 | L1 | pr_auc | 30 | 0.5000 | 0.0000 |
| random | mcar | M0 | L1 | precision_at_k | 30 | 0.5000 | 0.0000 |
| random | mcar | M0 | L1 | recall_at_k | 30 | 0.5000 | 0.0000 |
| random | mcar | M0 | L1 | roc_auc | 30 | 0.5000 | 0.0000 |
| random | mcar | M0 | L1g | pr_auc | 30 | 0.5000 | 0.0000 |
| random | mcar | M0 | L1g | precision_at_k | 30 | 0.5000 | 0.0000 |
| random | mcar | M0 | L1g | recall_at_k | 30 | 0.5000 | 0.0000 |
| random | mcar | M0 | L1g | roc_auc | 30 | 0.5000 | 0.0000 |
| random | mcar | M0 | L2 | pr_auc | 30 | 0.5000 | 0.0000 |
| random | mcar | M0 | L2 | precision_at_k | 30 | 0.5000 | 0.0000 |
| random | mcar | M0 | L2 | recall_at_k | 30 | 0.5000 | 0.0000 |
| random | mcar | M0 | L2 | roc_auc | 30 | 0.5000 | 0.0000 |
| random | mcar | M4c | L1 | pr_auc | 30 | 0.6909 | 0.0132 |
| random | mcar | M4c | L1 | precision_at_k | 30 | 0.6449 | 0.0091 |
| random | mcar | M4c | L1 | recall_at_k | 30 | 0.6449 | 0.0091 |
| random | mcar | M4c | L1 | roc_auc | 30 | 0.7008 | 0.0102 |
| random | mcar | M4c | L1g | pr_auc | 30 | 0.6914 | 0.0131 |
| random | mcar | M4c | L1g | precision_at_k | 30 | 0.6470 | 0.0095 |
| random | mcar | M4c | L1g | recall_at_k | 30 | 0.6470 | 0.0095 |
| random | mcar | M4c | L1g | roc_auc | 30 | 0.7029 | 0.0104 |
| random | mcar | M4c | L2 | pr_auc | 30 | 0.6219 | 0.0120 |
| random | mcar | M4c | L2 | precision_at_k | 30 | 0.5657 | 0.0101 |
| random | mcar | M4c | L2 | recall_at_k | 30 | 0.5657 | 0.0101 |
| random | mcar | M4c | L2 | roc_auc | 30 | 0.6126 | 0.0081 |
| random | mnar_out | M0 | L1 | pr_auc | 30 | 0.5000 | 0.0000 |
| random | mnar_out | M0 | L1 | precision_at_k | 30 | 0.5000 | 0.0000 |
| random | mnar_out | M0 | L1 | recall_at_k | 30 | 0.5000 | 0.0000 |
| random | mnar_out | M0 | L1 | roc_auc | 30 | 0.5000 | 0.0000 |
| random | mnar_out | M0 | L1g | pr_auc | 30 | 0.5000 | 0.0000 |
| random | mnar_out | M0 | L1g | precision_at_k | 30 | 0.5000 | 0.0000 |
| random | mnar_out | M0 | L1g | recall_at_k | 30 | 0.5000 | 0.0000 |
| random | mnar_out | M0 | L1g | roc_auc | 30 | 0.5000 | 0.0000 |
| random | mnar_out | M0 | L2 | pr_auc | 30 | 0.5000 | 0.0000 |
| random | mnar_out | M0 | L2 | precision_at_k | 30 | 0.5000 | 0.0000 |
| random | mnar_out | M0 | L2 | recall_at_k | 30 | 0.5000 | 0.0000 |
| random | mnar_out | M0 | L2 | roc_auc | 30 | 0.5000 | 0.0000 |
| random | mnar_out | M4c | L1 | pr_auc | 30 | 0.7179 | 0.0142 |
| random | mnar_out | M4c | L1 | precision_at_k | 30 | 0.6645 | 0.0103 |
| random | mnar_out | M4c | L1 | recall_at_k | 30 | 0.6645 | 0.0103 |
| random | mnar_out | M4c | L1 | roc_auc | 30 | 0.7297 | 0.0122 |
| random | mnar_out | M4c | L1g | pr_auc | 30 | 0.7182 | 0.0141 |
| random | mnar_out | M4c | L1g | precision_at_k | 30 | 0.6682 | 0.0112 |
| random | mnar_out | M4c | L1g | recall_at_k | 30 | 0.6682 | 0.0112 |
| random | mnar_out | M4c | L1g | roc_auc | 30 | 0.7315 | 0.0126 |
| random | mnar_out | M4c | L2 | pr_auc | 30 | 0.6305 | 0.0106 |
| random | mnar_out | M4c | L2 | precision_at_k | 30 | 0.5616 | 0.0082 |
| random | mnar_out | M4c | L2 | recall_at_k | 30 | 0.5616 | 0.0082 |
| random | mnar_out | M4c | L2 | roc_auc | 30 | 0.6199 | 0.0070 |
| sponsor_substitution | mcar | M0 | L1 | pr_auc | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mcar | M0 | L1 | precision_at_k | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mcar | M0 | L1 | recall_at_k | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mcar | M0 | L1 | roc_auc | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mcar | M0 | L1g | pr_auc | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mcar | M0 | L1g | precision_at_k | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mcar | M0 | L1g | recall_at_k | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mcar | M0 | L1g | roc_auc | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mcar | M0 | L2 | pr_auc | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mcar | M0 | L2 | precision_at_k | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mcar | M0 | L2 | recall_at_k | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mcar | M0 | L2 | roc_auc | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mcar | M4c | L1 | pr_auc | 30 | 0.4817 | 0.0111 |
| sponsor_substitution | mcar | M4c | L1 | precision_at_k | 30 | 0.4819 | 0.0132 |
| sponsor_substitution | mcar | M4c | L1 | recall_at_k | 30 | 0.4819 | 0.0132 |
| sponsor_substitution | mcar | M4c | L1 | roc_auc | 30 | 0.4718 | 0.0112 |
| sponsor_substitution | mcar | M4c | L1g | pr_auc | 30 | 0.4810 | 0.0109 |
| sponsor_substitution | mcar | M4c | L1g | precision_at_k | 30 | 0.4809 | 0.0125 |
| sponsor_substitution | mcar | M4c | L1g | recall_at_k | 30 | 0.4809 | 0.0125 |
| sponsor_substitution | mcar | M4c | L1g | roc_auc | 30 | 0.4714 | 0.0111 |
| sponsor_substitution | mcar | M4c | L2 | pr_auc | 30 | 0.4827 | 0.0080 |
| sponsor_substitution | mcar | M4c | L2 | precision_at_k | 30 | 0.4960 | 0.0075 |
| sponsor_substitution | mcar | M4c | L2 | recall_at_k | 30 | 0.4960 | 0.0075 |
| sponsor_substitution | mcar | M4c | L2 | roc_auc | 30 | 0.4838 | 0.0065 |
| sponsor_substitution | mnar_out | M0 | L1 | pr_auc | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mnar_out | M0 | L1 | precision_at_k | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mnar_out | M0 | L1 | recall_at_k | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mnar_out | M0 | L1 | roc_auc | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mnar_out | M0 | L1g | pr_auc | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mnar_out | M0 | L1g | precision_at_k | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mnar_out | M0 | L1g | recall_at_k | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mnar_out | M0 | L1g | roc_auc | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mnar_out | M0 | L2 | pr_auc | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mnar_out | M0 | L2 | precision_at_k | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mnar_out | M0 | L2 | recall_at_k | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mnar_out | M0 | L2 | roc_auc | 30 | 0.5000 | 0.0000 |
| sponsor_substitution | mnar_out | M4c | L1 | pr_auc | 30 | 0.4979 | 0.0132 |
| sponsor_substitution | mnar_out | M4c | L1 | precision_at_k | 30 | 0.5011 | 0.0117 |
| sponsor_substitution | mnar_out | M4c | L1 | recall_at_k | 30 | 0.5011 | 0.0117 |
| sponsor_substitution | mnar_out | M4c | L1 | roc_auc | 30 | 0.4926 | 0.0150 |
| sponsor_substitution | mnar_out | M4c | L1g | pr_auc | 30 | 0.4973 | 0.0131 |
| sponsor_substitution | mnar_out | M4c | L1g | precision_at_k | 30 | 0.4978 | 0.0127 |
| sponsor_substitution | mnar_out | M4c | L1g | recall_at_k | 30 | 0.4978 | 0.0127 |
| sponsor_substitution | mnar_out | M4c | L1g | roc_auc | 30 | 0.4913 | 0.0154 |
| sponsor_substitution | mnar_out | M4c | L2 | pr_auc | 30 | 0.4909 | 0.0097 |
| sponsor_substitution | mnar_out | M4c | L2 | precision_at_k | 30 | 0.5021 | 0.0069 |
| sponsor_substitution | mnar_out | M4c | L2 | recall_at_k | 30 | 0.5021 | 0.0069 |
| sponsor_substitution | mnar_out | M4c | L2 | roc_auc | 30 | 0.4935 | 0.0079 |

This L2 is a product of single-dyad conditional-pseudolikelihood scores, not the matched-marginal L2 used for the plan's dependence increment. No L3-F joint simulation, L3-C concept score, or native-event probability is reported here. Those require separate conditional simulation and target-specific analysis.
