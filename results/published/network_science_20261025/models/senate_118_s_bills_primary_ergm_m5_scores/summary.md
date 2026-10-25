# ERGM conditional footprint scores for native-event panels

- Dataset: `senate_118_s_bills_primary_ergm_m5_inputs`
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
| random | mcar | M4c | L1 | pr_auc | 30 | 0.7022 | 0.0137 |
| random | mcar | M4c | L1 | precision_at_k | 30 | 0.6690 | 0.0091 |
| random | mcar | M4c | L1 | recall_at_k | 30 | 0.6690 | 0.0091 |
| random | mcar | M4c | L1 | roc_auc | 30 | 0.7173 | 0.0082 |
| random | mcar | M4c | L1g | pr_auc | 30 | 0.7042 | 0.0133 |
| random | mcar | M4c | L1g | precision_at_k | 30 | 0.6740 | 0.0092 |
| random | mcar | M4c | L1g | recall_at_k | 30 | 0.6740 | 0.0092 |
| random | mcar | M4c | L1g | roc_auc | 30 | 0.7223 | 0.0076 |
| random | mcar | M4c | L2 | pr_auc | 30 | 0.5979 | 0.0092 |
| random | mcar | M4c | L2 | precision_at_k | 30 | 0.5607 | 0.0056 |
| random | mcar | M4c | L2 | recall_at_k | 30 | 0.5607 | 0.0056 |
| random | mcar | M4c | L2 | roc_auc | 30 | 0.6073 | 0.0065 |
| random | mcar | M5 | L1 | pr_auc | 30 | 0.7325 | 0.0109 |
| random | mcar | M5 | L1 | precision_at_k | 30 | 0.6736 | 0.0092 |
| random | mcar | M5 | L1 | recall_at_k | 30 | 0.6736 | 0.0092 |
| random | mcar | M5 | L1 | roc_auc | 30 | 0.7209 | 0.0088 |
| random | mcar | M5 | L1g | pr_auc | 30 | 0.7329 | 0.0110 |
| random | mcar | M5 | L1g | precision_at_k | 30 | 0.6804 | 0.0099 |
| random | mcar | M5 | L1g | recall_at_k | 30 | 0.6804 | 0.0099 |
| random | mcar | M5 | L1g | roc_auc | 30 | 0.7280 | 0.0084 |
| random | mcar | M5 | L2 | pr_auc | 30 | 0.6143 | 0.0097 |
| random | mcar | M5 | L2 | precision_at_k | 30 | 0.5833 | 0.0074 |
| random | mcar | M5 | L2 | recall_at_k | 30 | 0.5833 | 0.0074 |
| random | mcar | M5 | L2 | roc_auc | 30 | 0.6273 | 0.0073 |
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
| random | mnar_out | M4c | L1 | pr_auc | 30 | 0.7471 | 0.0151 |
| random | mnar_out | M4c | L1 | precision_at_k | 30 | 0.7075 | 0.0124 |
| random | mnar_out | M4c | L1 | recall_at_k | 30 | 0.7075 | 0.0124 |
| random | mnar_out | M4c | L1 | roc_auc | 30 | 0.7669 | 0.0112 |
| random | mnar_out | M4c | L1g | pr_auc | 30 | 0.7489 | 0.0152 |
| random | mnar_out | M4c | L1g | precision_at_k | 30 | 0.7109 | 0.0123 |
| random | mnar_out | M4c | L1g | recall_at_k | 30 | 0.7109 | 0.0123 |
| random | mnar_out | M4c | L1g | roc_auc | 30 | 0.7717 | 0.0114 |
| random | mnar_out | M4c | L2 | pr_auc | 30 | 0.6219 | 0.0107 |
| random | mnar_out | M4c | L2 | precision_at_k | 30 | 0.5812 | 0.0078 |
| random | mnar_out | M4c | L2 | recall_at_k | 30 | 0.5812 | 0.0078 |
| random | mnar_out | M4c | L2 | roc_auc | 30 | 0.6360 | 0.0079 |
| random | mnar_out | M5 | L1 | pr_auc | 30 | 0.7723 | 0.0138 |
| random | mnar_out | M5 | L1 | precision_at_k | 30 | 0.7055 | 0.0120 |
| random | mnar_out | M5 | L1 | recall_at_k | 30 | 0.7055 | 0.0120 |
| random | mnar_out | M5 | L1 | roc_auc | 30 | 0.7621 | 0.0128 |
| random | mnar_out | M5 | L1g | pr_auc | 30 | 0.7717 | 0.0142 |
| random | mnar_out | M5 | L1g | precision_at_k | 30 | 0.7107 | 0.0103 |
| random | mnar_out | M5 | L1g | recall_at_k | 30 | 0.7107 | 0.0103 |
| random | mnar_out | M5 | L1g | roc_auc | 30 | 0.7677 | 0.0130 |
| random | mnar_out | M5 | L2 | pr_auc | 30 | 0.6364 | 0.0129 |
| random | mnar_out | M5 | L2 | precision_at_k | 30 | 0.6031 | 0.0080 |
| random | mnar_out | M5 | L2 | recall_at_k | 30 | 0.6031 | 0.0080 |
| random | mnar_out | M5 | L2 | roc_auc | 30 | 0.6560 | 0.0093 |
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
| sponsor_substitution | mcar | M4c | L1 | pr_auc | 30 | 0.4710 | 0.0076 |
| sponsor_substitution | mcar | M4c | L1 | precision_at_k | 30 | 0.4742 | 0.0117 |
| sponsor_substitution | mcar | M4c | L1 | recall_at_k | 30 | 0.4742 | 0.0117 |
| sponsor_substitution | mcar | M4c | L1 | roc_auc | 30 | 0.4625 | 0.0107 |
| sponsor_substitution | mcar | M4c | L1g | pr_auc | 30 | 0.4716 | 0.0074 |
| sponsor_substitution | mcar | M4c | L1g | precision_at_k | 30 | 0.4747 | 0.0106 |
| sponsor_substitution | mcar | M4c | L1g | recall_at_k | 30 | 0.4747 | 0.0106 |
| sponsor_substitution | mcar | M4c | L1g | roc_auc | 30 | 0.4629 | 0.0106 |
| sponsor_substitution | mcar | M4c | L2 | pr_auc | 30 | 0.4794 | 0.0051 |
| sponsor_substitution | mcar | M4c | L2 | precision_at_k | 30 | 0.4927 | 0.0057 |
| sponsor_substitution | mcar | M4c | L2 | recall_at_k | 30 | 0.4927 | 0.0057 |
| sponsor_substitution | mcar | M4c | L2 | roc_auc | 30 | 0.4813 | 0.0054 |
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
| sponsor_substitution | mnar_out | M4c | L1 | pr_auc | 30 | 0.4857 | 0.0088 |
| sponsor_substitution | mnar_out | M4c | L1 | precision_at_k | 30 | 0.4987 | 0.0110 |
| sponsor_substitution | mnar_out | M4c | L1 | recall_at_k | 30 | 0.4987 | 0.0110 |
| sponsor_substitution | mnar_out | M4c | L1 | roc_auc | 30 | 0.4898 | 0.0112 |
| sponsor_substitution | mnar_out | M4c | L1g | pr_auc | 30 | 0.4854 | 0.0086 |
| sponsor_substitution | mnar_out | M4c | L1g | precision_at_k | 30 | 0.4977 | 0.0112 |
| sponsor_substitution | mnar_out | M4c | L1g | recall_at_k | 30 | 0.4977 | 0.0112 |
| sponsor_substitution | mnar_out | M4c | L1g | roc_auc | 30 | 0.4887 | 0.0110 |
| sponsor_substitution | mnar_out | M4c | L2 | pr_auc | 30 | 0.4875 | 0.0060 |
| sponsor_substitution | mnar_out | M4c | L2 | precision_at_k | 30 | 0.5005 | 0.0047 |
| sponsor_substitution | mnar_out | M4c | L2 | recall_at_k | 30 | 0.5005 | 0.0047 |
| sponsor_substitution | mnar_out | M4c | L2 | roc_auc | 30 | 0.4927 | 0.0049 |
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
