# ERGM conditional footprint scores for native-event panels

- Dataset: `senate_118_s_bills_primary_ergm_inputs`
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
| random | mcar | M4c_no_mutual | L1 | pr_auc | 30 | 0.6595 | 0.0145 |
| random | mcar | M4c_no_mutual | L1 | precision_at_k | 30 | 0.6209 | 0.0089 |
| random | mcar | M4c_no_mutual | L1 | recall_at_k | 30 | 0.6209 | 0.0089 |
| random | mcar | M4c_no_mutual | L1 | roc_auc | 30 | 0.6693 | 0.0105 |
| random | mcar | M4c_no_mutual | L1g | pr_auc | 30 | 0.6619 | 0.0143 |
| random | mcar | M4c_no_mutual | L1g | precision_at_k | 30 | 0.6271 | 0.0085 |
| random | mcar | M4c_no_mutual | L1g | recall_at_k | 30 | 0.6271 | 0.0085 |
| random | mcar | M4c_no_mutual | L1g | roc_auc | 30 | 0.6745 | 0.0099 |
| random | mcar | M4c_no_mutual | L2 | pr_auc | 30 | 0.5690 | 0.0092 |
| random | mcar | M4c_no_mutual | L2 | precision_at_k | 30 | 0.5430 | 0.0051 |
| random | mcar | M4c_no_mutual | L2 | recall_at_k | 30 | 0.5430 | 0.0051 |
| random | mcar | M4c_no_mutual | L2 | roc_auc | 30 | 0.5746 | 0.0058 |
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
| random | mnar_out | M4c_no_mutual | L1 | pr_auc | 30 | 0.7110 | 0.0145 |
| random | mnar_out | M4c_no_mutual | L1 | precision_at_k | 30 | 0.6732 | 0.0108 |
| random | mnar_out | M4c_no_mutual | L1 | recall_at_k | 30 | 0.6732 | 0.0108 |
| random | mnar_out | M4c_no_mutual | L1 | roc_auc | 30 | 0.7322 | 0.0115 |
| random | mnar_out | M4c_no_mutual | L1g | pr_auc | 30 | 0.7133 | 0.0144 |
| random | mnar_out | M4c_no_mutual | L1g | precision_at_k | 30 | 0.6757 | 0.0104 |
| random | mnar_out | M4c_no_mutual | L1g | recall_at_k | 30 | 0.6757 | 0.0104 |
| random | mnar_out | M4c_no_mutual | L1g | roc_auc | 30 | 0.7365 | 0.0118 |
| random | mnar_out | M4c_no_mutual | L2 | pr_auc | 30 | 0.5925 | 0.0093 |
| random | mnar_out | M4c_no_mutual | L2 | precision_at_k | 30 | 0.5618 | 0.0059 |
| random | mnar_out | M4c_no_mutual | L2 | recall_at_k | 30 | 0.5618 | 0.0059 |
| random | mnar_out | M4c_no_mutual | L2 | roc_auc | 30 | 0.6004 | 0.0068 |
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
| sponsor_substitution | mcar | M4c_no_mutual | L1 | pr_auc | 30 | 0.4587 | 0.0080 |
| sponsor_substitution | mcar | M4c_no_mutual | L1 | precision_at_k | 30 | 0.4590 | 0.0106 |
| sponsor_substitution | mcar | M4c_no_mutual | L1 | recall_at_k | 30 | 0.4590 | 0.0106 |
| sponsor_substitution | mcar | M4c_no_mutual | L1 | roc_auc | 30 | 0.4431 | 0.0112 |
| sponsor_substitution | mcar | M4c_no_mutual | L1g | pr_auc | 30 | 0.4586 | 0.0080 |
| sponsor_substitution | mcar | M4c_no_mutual | L1g | precision_at_k | 30 | 0.4589 | 0.0100 |
| sponsor_substitution | mcar | M4c_no_mutual | L1g | recall_at_k | 30 | 0.4589 | 0.0100 |
| sponsor_substitution | mcar | M4c_no_mutual | L1g | roc_auc | 30 | 0.4427 | 0.0115 |
| sponsor_substitution | mcar | M4c_no_mutual | L2 | pr_auc | 30 | 0.4744 | 0.0049 |
| sponsor_substitution | mcar | M4c_no_mutual | L2 | precision_at_k | 30 | 0.4880 | 0.0045 |
| sponsor_substitution | mcar | M4c_no_mutual | L2 | recall_at_k | 30 | 0.4880 | 0.0045 |
| sponsor_substitution | mcar | M4c_no_mutual | L2 | roc_auc | 30 | 0.4770 | 0.0050 |
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
| sponsor_substitution | mnar_out | M4c_no_mutual | L1 | pr_auc | 30 | 0.4752 | 0.0088 |
| sponsor_substitution | mnar_out | M4c_no_mutual | L1 | precision_at_k | 30 | 0.4885 | 0.0081 |
| sponsor_substitution | mnar_out | M4c_no_mutual | L1 | recall_at_k | 30 | 0.4885 | 0.0081 |
| sponsor_substitution | mnar_out | M4c_no_mutual | L1 | roc_auc | 30 | 0.4741 | 0.0111 |
| sponsor_substitution | mnar_out | M4c_no_mutual | L1g | pr_auc | 30 | 0.4740 | 0.0086 |
| sponsor_substitution | mnar_out | M4c_no_mutual | L1g | precision_at_k | 30 | 0.4846 | 0.0081 |
| sponsor_substitution | mnar_out | M4c_no_mutual | L1g | recall_at_k | 30 | 0.4846 | 0.0081 |
| sponsor_substitution | mnar_out | M4c_no_mutual | L1g | roc_auc | 30 | 0.4711 | 0.0108 |
| sponsor_substitution | mnar_out | M4c_no_mutual | L2 | pr_auc | 30 | 0.4819 | 0.0047 |
| sponsor_substitution | mnar_out | M4c_no_mutual | L2 | precision_at_k | 30 | 0.4957 | 0.0057 |
| sponsor_substitution | mnar_out | M4c_no_mutual | L2 | recall_at_k | 30 | 0.4957 | 0.0057 |
| sponsor_substitution | mnar_out | M4c_no_mutual | L2 | roc_auc | 30 | 0.4867 | 0.0040 |

This L2 is a product of single-dyad conditional-pseudolikelihood scores, not the matched-marginal L2 used for the plan's dependence increment. No L3-F joint simulation, L3-C concept score, or native-event probability is reported here. Those require separate conditional simulation and target-specific analysis.
