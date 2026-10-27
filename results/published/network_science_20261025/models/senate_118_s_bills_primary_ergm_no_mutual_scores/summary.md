# ERGM conditional footprint scores for native-event panels

- Dataset: `senate_118_s_bills_primary_ergm_inputs`
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
| random | mcar | M4c | L1 | pr_auc | 30 | 0.6883 | 0.0144 |
| random | mcar | M4c | L1 | precision_at_k | 30 | 0.6618 | 0.0112 |
| random | mcar | M4c | L1 | recall_at_k | 30 | 0.6618 | 0.0112 |
| random | mcar | M4c | L1 | roc_auc | 30 | 0.7062 | 0.0093 |
| random | mcar | M4c | L1g | pr_auc | 30 | 0.6899 | 0.0144 |
| random | mcar | M4c | L1g | precision_at_k | 30 | 0.6664 | 0.0090 |
| random | mcar | M4c | L1g | recall_at_k | 30 | 0.6664 | 0.0090 |
| random | mcar | M4c | L1g | roc_auc | 30 | 0.7103 | 0.0092 |
| random | mcar | M4c | L2 | pr_auc | 30 | 0.5866 | 0.0102 |
| random | mcar | M4c | L2 | precision_at_k | 30 | 0.5524 | 0.0061 |
| random | mcar | M4c | L2 | recall_at_k | 30 | 0.5524 | 0.0061 |
| random | mcar | M4c | L2 | roc_auc | 30 | 0.5966 | 0.0045 |
| random | mcar | M4c_no_mutual | L1 | pr_auc | 30 | 0.6467 | 0.0144 |
| random | mcar | M4c_no_mutual | L1 | precision_at_k | 30 | 0.6146 | 0.0107 |
| random | mcar | M4c_no_mutual | L1 | recall_at_k | 30 | 0.6146 | 0.0107 |
| random | mcar | M4c_no_mutual | L1 | roc_auc | 30 | 0.6571 | 0.0101 |
| random | mcar | M4c_no_mutual | L1g | pr_auc | 30 | 0.6482 | 0.0145 |
| random | mcar | M4c_no_mutual | L1g | precision_at_k | 30 | 0.6195 | 0.0101 |
| random | mcar | M4c_no_mutual | L1g | recall_at_k | 30 | 0.6195 | 0.0101 |
| random | mcar | M4c_no_mutual | L1g | roc_auc | 30 | 0.6612 | 0.0102 |
| random | mcar | M4c_no_mutual | L2 | pr_auc | 30 | 0.5590 | 0.0095 |
| random | mcar | M4c_no_mutual | L2 | precision_at_k | 30 | 0.5348 | 0.0065 |
| random | mcar | M4c_no_mutual | L2 | recall_at_k | 30 | 0.5348 | 0.0065 |
| random | mcar | M4c_no_mutual | L2 | roc_auc | 30 | 0.5641 | 0.0044 |
| random | mnar_out | M4c | L1 | pr_auc | 30 | 0.7418 | 0.0139 |
| random | mnar_out | M4c | L1 | precision_at_k | 30 | 0.7028 | 0.0104 |
| random | mnar_out | M4c | L1 | recall_at_k | 30 | 0.7028 | 0.0104 |
| random | mnar_out | M4c | L1 | roc_auc | 30 | 0.7605 | 0.0088 |
| random | mnar_out | M4c | L1g | pr_auc | 30 | 0.7431 | 0.0140 |
| random | mnar_out | M4c | L1g | precision_at_k | 30 | 0.7063 | 0.0102 |
| random | mnar_out | M4c | L1g | recall_at_k | 30 | 0.7063 | 0.0102 |
| random | mnar_out | M4c | L1g | roc_auc | 30 | 0.7644 | 0.0089 |
| random | mnar_out | M4c | L2 | pr_auc | 30 | 0.6155 | 0.0091 |
| random | mnar_out | M4c | L2 | precision_at_k | 30 | 0.5732 | 0.0069 |
| random | mnar_out | M4c | L2 | recall_at_k | 30 | 0.5732 | 0.0069 |
| random | mnar_out | M4c | L2 | roc_auc | 30 | 0.6264 | 0.0050 |
| random | mnar_out | M4c_no_mutual | L1 | pr_auc | 30 | 0.7051 | 0.0145 |
| random | mnar_out | M4c_no_mutual | L1 | precision_at_k | 30 | 0.6689 | 0.0085 |
| random | mnar_out | M4c_no_mutual | L1 | recall_at_k | 30 | 0.6689 | 0.0085 |
| random | mnar_out | M4c_no_mutual | L1 | roc_auc | 30 | 0.7249 | 0.0099 |
| random | mnar_out | M4c_no_mutual | L1g | pr_auc | 30 | 0.7070 | 0.0146 |
| random | mnar_out | M4c_no_mutual | L1g | precision_at_k | 30 | 0.6717 | 0.0100 |
| random | mnar_out | M4c_no_mutual | L1g | recall_at_k | 30 | 0.6717 | 0.0100 |
| random | mnar_out | M4c_no_mutual | L1g | roc_auc | 30 | 0.7283 | 0.0101 |
| random | mnar_out | M4c_no_mutual | L2 | pr_auc | 30 | 0.5855 | 0.0097 |
| random | mnar_out | M4c_no_mutual | L2 | precision_at_k | 30 | 0.5536 | 0.0070 |
| random | mnar_out | M4c_no_mutual | L2 | recall_at_k | 30 | 0.5536 | 0.0070 |
| random | mnar_out | M4c_no_mutual | L2 | roc_auc | 30 | 0.5905 | 0.0051 |
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

## Aggregate MPLE numerical diagnostics

No coefficient-inference claim is made. Models use MPLE without coefficient regularization or input standardization.
The table reports fitting and conditional-score stability only; no coefficient values are released.

| Model | fits attempted/scored | failures | fit/prediction warnings | nonfinite coefficients | max $|\hat\theta|$ | exact $p=0/1$ |
|---|---:|---:|---:|---:|---:|---:|
| M4c | 60/60 | 0 | 0/0 | 0 | 85.034 | 0/0 |
| M4c_no_mutual | 60/60 | 0 | 0/0 | 0 | 82.059 | 0/0 |
