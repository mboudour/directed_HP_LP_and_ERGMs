# ERGM conditional footprint scores for native-event panels

- Dataset: `senate_118_s_bills_cap3_sensitivity_ergm_inputs`
- Each static ERGM is fit separately to a frozen event-first observed projection.
- L1 is the arithmetic mean of conditional-pseudolikelihood dyad scores; L1g is their geometric mean; L2 is their product.
- L2 metrics use `log_L2`, a strictly monotone numeric representation of the L2 product.
- These scores estimate **graph-footprint completion**, not the probability that a recorded native event occurred.

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
| random | mcar | M4c | L1 | pr_auc | 30 | 0.6772 | 0.0150 |
| random | mcar | M4c | L1 | precision_at_k | 30 | 0.6382 | 0.0117 |
| random | mcar | M4c | L1 | recall_at_k | 30 | 0.6382 | 0.0117 |
| random | mcar | M4c | L1 | roc_auc | 30 | 0.6877 | 0.0136 |
| random | mcar | M4c | L1g | pr_auc | 30 | 0.6773 | 0.0148 |
| random | mcar | M4c | L1g | precision_at_k | 30 | 0.6396 | 0.0122 |
| random | mcar | M4c | L1g | recall_at_k | 30 | 0.6396 | 0.0122 |
| random | mcar | M4c | L1g | roc_auc | 30 | 0.6891 | 0.0135 |
| random | mcar | M4c | L2 | pr_auc | 30 | 0.6117 | 0.0118 |
| random | mcar | M4c | L2 | precision_at_k | 30 | 0.5604 | 0.0082 |
| random | mcar | M4c | L2 | recall_at_k | 30 | 0.5604 | 0.0082 |
| random | mcar | M4c | L2 | roc_auc | 30 | 0.6026 | 0.0076 |
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
| random | mnar_out | M4c | L1 | pr_auc | 30 | 0.7096 | 0.0160 |
| random | mnar_out | M4c | L1 | precision_at_k | 30 | 0.6600 | 0.0086 |
| random | mnar_out | M4c | L1 | recall_at_k | 30 | 0.6600 | 0.0086 |
| random | mnar_out | M4c | L1 | roc_auc | 30 | 0.7205 | 0.0118 |
| random | mnar_out | M4c | L1g | pr_auc | 30 | 0.7099 | 0.0158 |
| random | mnar_out | M4c | L1g | precision_at_k | 30 | 0.6640 | 0.0087 |
| random | mnar_out | M4c | L1g | recall_at_k | 30 | 0.6640 | 0.0087 |
| random | mnar_out | M4c | L1g | roc_auc | 30 | 0.7222 | 0.0119 |
| random | mnar_out | M4c | L2 | pr_auc | 30 | 0.6235 | 0.0109 |
| random | mnar_out | M4c | L2 | precision_at_k | 30 | 0.5570 | 0.0097 |
| random | mnar_out | M4c | L2 | recall_at_k | 30 | 0.5570 | 0.0097 |
| random | mnar_out | M4c | L2 | roc_auc | 30 | 0.6113 | 0.0068 |
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

## Aggregate MPLE numerical diagnostics

No coefficient-inference claim is made. Models use MPLE without coefficient regularization or input standardization.
The table reports fitting and conditional-score stability only; no coefficient values are released.

| Model | fits attempted/scored | failures | fit/prediction warnings | nonfinite coefficients | max $|\hat\theta|$ | exact $p=0/1$ |
|---|---:|---:|---:|---:|---:|---:|
| M0 | 60/60 | 0 | 0/0 | 0 | 1.559 | 0/0 |
| M4c | 60/60 | 0 | 0/0 | 0 | 12.762 | 0/0 |
