# ERGM conditional footprint scores for native-event panels

- Dataset: `senate_118_s_bills_primary_ergm_m5_inputs`
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
| random | mcar | M5 | L1 | pr_auc | 30 | 0.7210 | 0.0120 |
| random | mcar | M5 | L1 | precision_at_k | 30 | 0.6669 | 0.0097 |
| random | mcar | M5 | L1 | recall_at_k | 30 | 0.6669 | 0.0097 |
| random | mcar | M5 | L1 | roc_auc | 30 | 0.7102 | 0.0097 |
| random | mcar | M5 | L1g | pr_auc | 30 | 0.7207 | 0.0122 |
| random | mcar | M5 | L1g | precision_at_k | 30 | 0.6744 | 0.0104 |
| random | mcar | M5 | L1g | recall_at_k | 30 | 0.6744 | 0.0104 |
| random | mcar | M5 | L1g | roc_auc | 30 | 0.7165 | 0.0095 |
| random | mcar | M5 | L2 | pr_auc | 30 | 0.6039 | 0.0099 |
| random | mcar | M5 | L2 | precision_at_k | 30 | 0.5764 | 0.0081 |
| random | mcar | M5 | L2 | recall_at_k | 30 | 0.5764 | 0.0081 |
| random | mcar | M5 | L2 | roc_auc | 30 | 0.6164 | 0.0056 |
| random | mnar_out | M5 | L1 | pr_auc | 30 | 0.7679 | 0.0129 |
| random | mnar_out | M5 | L1 | precision_at_k | 30 | 0.7015 | 0.0093 |
| random | mnar_out | M5 | L1 | recall_at_k | 30 | 0.7015 | 0.0093 |
| random | mnar_out | M5 | L1 | roc_auc | 30 | 0.7563 | 0.0100 |
| random | mnar_out | M5 | L1g | pr_auc | 30 | 0.7668 | 0.0131 |
| random | mnar_out | M5 | L1g | precision_at_k | 30 | 0.7060 | 0.0093 |
| random | mnar_out | M5 | L1g | recall_at_k | 30 | 0.7060 | 0.0093 |
| random | mnar_out | M5 | L1g | roc_auc | 30 | 0.7609 | 0.0102 |
| random | mnar_out | M5 | L2 | pr_auc | 30 | 0.6299 | 0.0102 |
| random | mnar_out | M5 | L2 | precision_at_k | 30 | 0.5962 | 0.0064 |
| random | mnar_out | M5 | L2 | recall_at_k | 30 | 0.5962 | 0.0064 |
| random | mnar_out | M5 | L2 | roc_auc | 30 | 0.6465 | 0.0063 |
| sponsor_substitution | mcar | M5 | L1 | pr_auc | 30 | 0.4914 | 0.0067 |
| sponsor_substitution | mcar | M5 | L1 | precision_at_k | 30 | 0.4872 | 0.0107 |
| sponsor_substitution | mcar | M5 | L1 | recall_at_k | 30 | 0.4872 | 0.0107 |
| sponsor_substitution | mcar | M5 | L1 | roc_auc | 30 | 0.4820 | 0.0096 |
| sponsor_substitution | mcar | M5 | L1g | pr_auc | 30 | 0.4895 | 0.0066 |
| sponsor_substitution | mcar | M5 | L1g | precision_at_k | 30 | 0.4864 | 0.0093 |
| sponsor_substitution | mcar | M5 | L1g | recall_at_k | 30 | 0.4864 | 0.0093 |
| sponsor_substitution | mcar | M5 | L1g | roc_auc | 30 | 0.4801 | 0.0096 |
| sponsor_substitution | mcar | M5 | L2 | pr_auc | 30 | 0.4879 | 0.0046 |
| sponsor_substitution | mcar | M5 | L2 | precision_at_k | 30 | 0.4973 | 0.0076 |
| sponsor_substitution | mcar | M5 | L2 | recall_at_k | 30 | 0.4973 | 0.0076 |
| sponsor_substitution | mcar | M5 | L2 | roc_auc | 30 | 0.4883 | 0.0058 |
| sponsor_substitution | mnar_out | M5 | L1 | pr_auc | 30 | 0.5087 | 0.0065 |
| sponsor_substitution | mnar_out | M5 | L1 | precision_at_k | 30 | 0.5072 | 0.0098 |
| sponsor_substitution | mnar_out | M5 | L1 | recall_at_k | 30 | 0.5072 | 0.0098 |
| sponsor_substitution | mnar_out | M5 | L1 | roc_auc | 30 | 0.5041 | 0.0085 |
| sponsor_substitution | mnar_out | M5 | L1g | pr_auc | 30 | 0.5050 | 0.0065 |
| sponsor_substitution | mnar_out | M5 | L1g | precision_at_k | 30 | 0.5067 | 0.0086 |
| sponsor_substitution | mnar_out | M5 | L1g | recall_at_k | 30 | 0.5067 | 0.0086 |
| sponsor_substitution | mnar_out | M5 | L1g | roc_auc | 30 | 0.5006 | 0.0087 |
| sponsor_substitution | mnar_out | M5 | L2 | pr_auc | 30 | 0.4966 | 0.0047 |
| sponsor_substitution | mnar_out | M5 | L2 | precision_at_k | 30 | 0.5045 | 0.0055 |
| sponsor_substitution | mnar_out | M5 | L2 | recall_at_k | 30 | 0.5045 | 0.0055 |
| sponsor_substitution | mnar_out | M5 | L2 | roc_auc | 30 | 0.5001 | 0.0044 |

This L2 is a product of single-dyad conditional-pseudolikelihood scores, not the matched-marginal L2 used for the plan's dependence increment. No L3-F joint simulation, L3-C concept score, or native-event probability is reported here. Those require separate conditional simulation and target-specific analysis.

## Aggregate MPLE numerical diagnostics

No coefficient-inference claim is made. Models use MPLE without coefficient regularization or input standardization.
The table reports fitting and conditional-score stability only; no coefficient values are released.

| Model | fits attempted/scored | failures | fit/prediction warnings | nonfinite coefficients | max $|\hat\theta|$ | exact $p=0/1$ |
|---|---:|---:|---:|---:|---:|---:|
| M5 | 60/60 | 0 | 0/0 | 0 | 95.495 | 0/0 |
