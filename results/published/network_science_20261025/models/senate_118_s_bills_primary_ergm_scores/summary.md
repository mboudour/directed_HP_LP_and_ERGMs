# ERGM conditional footprint scores for native-event panels

- Dataset: `senate_118_s_bills_primary_ergm_inputs`
- Each static ERGM is fit separately to a frozen event-first observed projection.
- L1 is the arithmetic mean of conditional-pseudolikelihood dyad scores; L1g is their geometric mean; L2 is their product.
- L2 metrics use `log_L2`, a strictly monotone numeric representation of the L2 product.
- These scores estimate **graph-footprint completion**, not the probability that a recorded native event occurred.

## Completion status

- Frozen splits: 60 (completed without model failure: 59)
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
| random | mcar | M1 | L1 | pr_auc | 30 | 0.6565 | 0.0094 |
| random | mcar | M1 | L1 | precision_at_k | 30 | 0.6723 | 0.0081 |
| random | mcar | M1 | L1 | recall_at_k | 30 | 0.6723 | 0.0081 |
| random | mcar | M1 | L1 | roc_auc | 30 | 0.6928 | 0.0089 |
| random | mcar | M1 | L1g | pr_auc | 30 | 0.6565 | 0.0094 |
| random | mcar | M1 | L1g | precision_at_k | 30 | 0.6723 | 0.0081 |
| random | mcar | M1 | L1g | recall_at_k | 30 | 0.6723 | 0.0081 |
| random | mcar | M1 | L1g | roc_auc | 30 | 0.6928 | 0.0089 |
| random | mcar | M1 | L2 | pr_auc | 30 | 0.5641 | 0.0060 |
| random | mcar | M1 | L2 | precision_at_k | 30 | 0.5419 | 0.0043 |
| random | mcar | M1 | L2 | recall_at_k | 30 | 0.5419 | 0.0043 |
| random | mcar | M1 | L2 | roc_auc | 30 | 0.5794 | 0.0032 |
| random | mcar | M2 | L1 | pr_auc | 30 | 0.6908 | 0.0132 |
| random | mcar | M2 | L1 | precision_at_k | 30 | 0.6795 | 0.0091 |
| random | mcar | M2 | L1 | recall_at_k | 30 | 0.6795 | 0.0091 |
| random | mcar | M2 | L1 | roc_auc | 30 | 0.7156 | 0.0089 |
| random | mcar | M2 | L1g | pr_auc | 30 | 0.6909 | 0.0132 |
| random | mcar | M2 | L1g | precision_at_k | 30 | 0.6797 | 0.0091 |
| random | mcar | M2 | L1g | recall_at_k | 30 | 0.6797 | 0.0091 |
| random | mcar | M2 | L1g | roc_auc | 30 | 0.7157 | 0.0089 |
| random | mcar | M2 | L2 | pr_auc | 30 | 0.5949 | 0.0101 |
| random | mcar | M2 | L2 | precision_at_k | 30 | 0.5489 | 0.0060 |
| random | mcar | M2 | L2 | recall_at_k | 30 | 0.5489 | 0.0060 |
| random | mcar | M2 | L2 | roc_auc | 30 | 0.5906 | 0.0057 |
| random | mcar | M3 | L1 | pr_auc | 29 | 0.6594 | 0.0125 |
| random | mcar | M3 | L1 | precision_at_k | 29 | 0.6742 | 0.0082 |
| random | mcar | M3 | L1 | recall_at_k | 29 | 0.6742 | 0.0082 |
| random | mcar | M3 | L1 | roc_auc | 29 | 0.6934 | 0.0099 |
| random | mcar | M3 | L1g | pr_auc | 29 | 0.6596 | 0.0124 |
| random | mcar | M3 | L1g | precision_at_k | 29 | 0.6748 | 0.0082 |
| random | mcar | M3 | L1g | recall_at_k | 29 | 0.6748 | 0.0082 |
| random | mcar | M3 | L1g | roc_auc | 29 | 0.6940 | 0.0098 |
| random | mcar | M3 | L2 | pr_auc | 29 | 0.5681 | 0.0100 |
| random | mcar | M3 | L2 | precision_at_k | 29 | 0.5442 | 0.0057 |
| random | mcar | M3 | L2 | recall_at_k | 29 | 0.5442 | 0.0057 |
| random | mcar | M3 | L2 | roc_auc | 29 | 0.5791 | 0.0058 |
| random | mcar | M4 | L1 | pr_auc | 30 | 0.6607 | 0.0139 |
| random | mcar | M4 | L1 | precision_at_k | 30 | 0.6719 | 0.0100 |
| random | mcar | M4 | L1 | recall_at_k | 30 | 0.6719 | 0.0100 |
| random | mcar | M4 | L1 | roc_auc | 30 | 0.6927 | 0.0105 |
| random | mcar | M4 | L1g | pr_auc | 30 | 0.6608 | 0.0139 |
| random | mcar | M4 | L1g | precision_at_k | 30 | 0.6724 | 0.0101 |
| random | mcar | M4 | L1g | recall_at_k | 30 | 0.6724 | 0.0101 |
| random | mcar | M4 | L1g | roc_auc | 30 | 0.6933 | 0.0104 |
| random | mcar | M4 | L2 | pr_auc | 30 | 0.5697 | 0.0099 |
| random | mcar | M4 | L2 | precision_at_k | 30 | 0.5443 | 0.0059 |
| random | mcar | M4 | L2 | recall_at_k | 30 | 0.5443 | 0.0059 |
| random | mcar | M4 | L2 | roc_auc | 30 | 0.5792 | 0.0042 |
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
| random | mnar_out | M1 | L1 | pr_auc | 30 | 0.6868 | 0.0114 |
| random | mnar_out | M1 | L1 | precision_at_k | 30 | 0.6984 | 0.0094 |
| random | mnar_out | M1 | L1 | recall_at_k | 30 | 0.6984 | 0.0094 |
| random | mnar_out | M1 | L1 | roc_auc | 30 | 0.7258 | 0.0107 |
| random | mnar_out | M1 | L1g | pr_auc | 30 | 0.6868 | 0.0114 |
| random | mnar_out | M1 | L1g | precision_at_k | 30 | 0.6984 | 0.0094 |
| random | mnar_out | M1 | L1g | recall_at_k | 30 | 0.6984 | 0.0094 |
| random | mnar_out | M1 | L1g | roc_auc | 30 | 0.7258 | 0.0107 |
| random | mnar_out | M1 | L2 | pr_auc | 30 | 0.5777 | 0.0065 |
| random | mnar_out | M1 | L2 | precision_at_k | 30 | 0.5534 | 0.0072 |
| random | mnar_out | M1 | L2 | recall_at_k | 30 | 0.5534 | 0.0072 |
| random | mnar_out | M1 | L2 | roc_auc | 30 | 0.5949 | 0.0044 |
| random | mnar_out | M2 | L1 | pr_auc | 30 | 0.7275 | 0.0129 |
| random | mnar_out | M2 | L1 | precision_at_k | 30 | 0.7122 | 0.0105 |
| random | mnar_out | M2 | L1 | recall_at_k | 30 | 0.7122 | 0.0105 |
| random | mnar_out | M2 | L1 | roc_auc | 30 | 0.7520 | 0.0099 |
| random | mnar_out | M2 | L1g | pr_auc | 30 | 0.7275 | 0.0129 |
| random | mnar_out | M2 | L1g | precision_at_k | 30 | 0.7120 | 0.0104 |
| random | mnar_out | M2 | L1g | recall_at_k | 30 | 0.7120 | 0.0104 |
| random | mnar_out | M2 | L1g | roc_auc | 30 | 0.7519 | 0.0099 |
| random | mnar_out | M2 | L2 | pr_auc | 30 | 0.6149 | 0.0076 |
| random | mnar_out | M2 | L2 | precision_at_k | 30 | 0.5578 | 0.0071 |
| random | mnar_out | M2 | L2 | recall_at_k | 30 | 0.5578 | 0.0071 |
| random | mnar_out | M2 | L2 | roc_auc | 30 | 0.6067 | 0.0039 |
| random | mnar_out | M3 | L1 | pr_auc | 30 | 0.6843 | 0.0139 |
| random | mnar_out | M3 | L1 | precision_at_k | 30 | 0.6943 | 0.0105 |
| random | mnar_out | M3 | L1 | recall_at_k | 30 | 0.6943 | 0.0105 |
| random | mnar_out | M3 | L1 | roc_auc | 30 | 0.7227 | 0.0115 |
| random | mnar_out | M3 | L1g | pr_auc | 30 | 0.6844 | 0.0139 |
| random | mnar_out | M3 | L1g | precision_at_k | 30 | 0.6948 | 0.0103 |
| random | mnar_out | M3 | L1g | recall_at_k | 30 | 0.6948 | 0.0103 |
| random | mnar_out | M3 | L1g | roc_auc | 30 | 0.7230 | 0.0114 |
| random | mnar_out | M3 | L2 | pr_auc | 30 | 0.5766 | 0.0098 |
| random | mnar_out | M3 | L2 | precision_at_k | 30 | 0.5544 | 0.0064 |
| random | mnar_out | M3 | L2 | recall_at_k | 30 | 0.5544 | 0.0064 |
| random | mnar_out | M3 | L2 | roc_auc | 30 | 0.5913 | 0.0044 |
| random | mnar_out | M4 | L1 | pr_auc | 30 | 0.6859 | 0.0116 |
| random | mnar_out | M4 | L1 | precision_at_k | 30 | 0.6958 | 0.0102 |
| random | mnar_out | M4 | L1 | recall_at_k | 30 | 0.6958 | 0.0102 |
| random | mnar_out | M4 | L1 | roc_auc | 30 | 0.7241 | 0.0103 |
| random | mnar_out | M4 | L1g | pr_auc | 30 | 0.6860 | 0.0116 |
| random | mnar_out | M4 | L1g | precision_at_k | 30 | 0.6957 | 0.0103 |
| random | mnar_out | M4 | L1g | recall_at_k | 30 | 0.6957 | 0.0103 |
| random | mnar_out | M4 | L1g | roc_auc | 30 | 0.7244 | 0.0104 |
| random | mnar_out | M4 | L2 | pr_auc | 30 | 0.5773 | 0.0065 |
| random | mnar_out | M4 | L2 | precision_at_k | 30 | 0.5549 | 0.0069 |
| random | mnar_out | M4 | L2 | recall_at_k | 30 | 0.5549 | 0.0069 |
| random | mnar_out | M4 | L2 | roc_auc | 30 | 0.5919 | 0.0035 |
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
| sponsor_substitution | mcar | M1 | L1 | pr_auc | 30 | 0.4922 | 0.0061 |
| sponsor_substitution | mcar | M1 | L1 | precision_at_k | 30 | 0.4906 | 0.0089 |
| sponsor_substitution | mcar | M1 | L1 | recall_at_k | 30 | 0.4906 | 0.0089 |
| sponsor_substitution | mcar | M1 | L1 | roc_auc | 30 | 0.4872 | 0.0096 |
| sponsor_substitution | mcar | M1 | L1g | pr_auc | 30 | 0.4922 | 0.0061 |
| sponsor_substitution | mcar | M1 | L1g | precision_at_k | 30 | 0.4906 | 0.0089 |
| sponsor_substitution | mcar | M1 | L1g | recall_at_k | 30 | 0.4906 | 0.0089 |
| sponsor_substitution | mcar | M1 | L1g | roc_auc | 30 | 0.4872 | 0.0096 |
| sponsor_substitution | mcar | M1 | L2 | pr_auc | 30 | 0.4941 | 0.0038 |
| sponsor_substitution | mcar | M1 | L2 | precision_at_k | 30 | 0.4993 | 0.0047 |
| sponsor_substitution | mcar | M1 | L2 | recall_at_k | 30 | 0.4993 | 0.0047 |
| sponsor_substitution | mcar | M1 | L2 | roc_auc | 30 | 0.4944 | 0.0041 |
| sponsor_substitution | mcar | M2 | L1 | pr_auc | 30 | 0.5096 | 0.0084 |
| sponsor_substitution | mcar | M2 | L1 | precision_at_k | 30 | 0.4936 | 0.0093 |
| sponsor_substitution | mcar | M2 | L1 | recall_at_k | 30 | 0.4936 | 0.0093 |
| sponsor_substitution | mcar | M2 | L1 | roc_auc | 30 | 0.4994 | 0.0102 |
| sponsor_substitution | mcar | M2 | L1g | pr_auc | 30 | 0.5096 | 0.0084 |
| sponsor_substitution | mcar | M2 | L1g | precision_at_k | 30 | 0.4937 | 0.0092 |
| sponsor_substitution | mcar | M2 | L1g | recall_at_k | 30 | 0.4937 | 0.0092 |
| sponsor_substitution | mcar | M2 | L1g | roc_auc | 30 | 0.4994 | 0.0102 |
| sponsor_substitution | mcar | M2 | L2 | pr_auc | 30 | 0.5049 | 0.0057 |
| sponsor_substitution | mcar | M2 | L2 | precision_at_k | 30 | 0.5007 | 0.0047 |
| sponsor_substitution | mcar | M2 | L2 | recall_at_k | 30 | 0.5007 | 0.0047 |
| sponsor_substitution | mcar | M2 | L2 | roc_auc | 30 | 0.5001 | 0.0041 |
| sponsor_substitution | mcar | M3 | L1 | pr_auc | 29 | 0.4839 | 0.0098 |
| sponsor_substitution | mcar | M3 | L1 | precision_at_k | 29 | 0.4912 | 0.0099 |
| sponsor_substitution | mcar | M3 | L1 | recall_at_k | 29 | 0.4912 | 0.0099 |
| sponsor_substitution | mcar | M3 | L1 | roc_auc | 29 | 0.4818 | 0.0110 |
| sponsor_substitution | mcar | M3 | L1g | pr_auc | 29 | 0.4839 | 0.0096 |
| sponsor_substitution | mcar | M3 | L1g | precision_at_k | 29 | 0.4912 | 0.0097 |
| sponsor_substitution | mcar | M3 | L1g | recall_at_k | 29 | 0.4912 | 0.0097 |
| sponsor_substitution | mcar | M3 | L1g | roc_auc | 29 | 0.4819 | 0.0108 |
| sponsor_substitution | mcar | M3 | L2 | pr_auc | 29 | 0.4890 | 0.0062 |
| sponsor_substitution | mcar | M3 | L2 | precision_at_k | 29 | 0.4999 | 0.0053 |
| sponsor_substitution | mcar | M3 | L2 | recall_at_k | 29 | 0.4999 | 0.0053 |
| sponsor_substitution | mcar | M3 | L2 | roc_auc | 29 | 0.4924 | 0.0042 |
| sponsor_substitution | mcar | M4 | L1 | pr_auc | 30 | 0.4926 | 0.0108 |
| sponsor_substitution | mcar | M4 | L1 | precision_at_k | 30 | 0.4943 | 0.0102 |
| sponsor_substitution | mcar | M4 | L1 | recall_at_k | 30 | 0.4943 | 0.0102 |
| sponsor_substitution | mcar | M4 | L1 | roc_auc | 30 | 0.4908 | 0.0128 |
| sponsor_substitution | mcar | M4 | L1g | pr_auc | 30 | 0.4927 | 0.0108 |
| sponsor_substitution | mcar | M4 | L1g | precision_at_k | 30 | 0.4940 | 0.0106 |
| sponsor_substitution | mcar | M4 | L1g | recall_at_k | 30 | 0.4940 | 0.0106 |
| sponsor_substitution | mcar | M4 | L1g | roc_auc | 30 | 0.4910 | 0.0129 |
| sponsor_substitution | mcar | M4 | L2 | pr_auc | 30 | 0.4935 | 0.0062 |
| sponsor_substitution | mcar | M4 | L2 | precision_at_k | 30 | 0.4997 | 0.0056 |
| sponsor_substitution | mcar | M4 | L2 | recall_at_k | 30 | 0.4997 | 0.0056 |
| sponsor_substitution | mcar | M4 | L2 | roc_auc | 30 | 0.4962 | 0.0053 |
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
| sponsor_substitution | mnar_out | M1 | L1 | pr_auc | 30 | 0.5038 | 0.0060 |
| sponsor_substitution | mnar_out | M1 | L1 | precision_at_k | 30 | 0.5083 | 0.0088 |
| sponsor_substitution | mnar_out | M1 | L1 | recall_at_k | 30 | 0.5083 | 0.0088 |
| sponsor_substitution | mnar_out | M1 | L1 | roc_auc | 30 | 0.5065 | 0.0094 |
| sponsor_substitution | mnar_out | M1 | L1g | pr_auc | 30 | 0.5038 | 0.0060 |
| sponsor_substitution | mnar_out | M1 | L1g | precision_at_k | 30 | 0.5083 | 0.0088 |
| sponsor_substitution | mnar_out | M1 | L1g | recall_at_k | 30 | 0.5083 | 0.0088 |
| sponsor_substitution | mnar_out | M1 | L1g | roc_auc | 30 | 0.5065 | 0.0094 |
| sponsor_substitution | mnar_out | M1 | L2 | pr_auc | 30 | 0.4991 | 0.0043 |
| sponsor_substitution | mnar_out | M1 | L2 | precision_at_k | 30 | 0.5053 | 0.0051 |
| sponsor_substitution | mnar_out | M1 | L2 | recall_at_k | 30 | 0.5053 | 0.0051 |
| sponsor_substitution | mnar_out | M1 | L2 | roc_auc | 30 | 0.5032 | 0.0041 |
| sponsor_substitution | mnar_out | M2 | L1 | pr_auc | 30 | 0.5191 | 0.0100 |
| sponsor_substitution | mnar_out | M2 | L1 | precision_at_k | 30 | 0.5093 | 0.0094 |
| sponsor_substitution | mnar_out | M2 | L1 | recall_at_k | 30 | 0.5093 | 0.0094 |
| sponsor_substitution | mnar_out | M2 | L1 | roc_auc | 30 | 0.5167 | 0.0104 |
| sponsor_substitution | mnar_out | M2 | L1g | pr_auc | 30 | 0.5191 | 0.0100 |
| sponsor_substitution | mnar_out | M2 | L1g | precision_at_k | 30 | 0.5093 | 0.0095 |
| sponsor_substitution | mnar_out | M2 | L1g | recall_at_k | 30 | 0.5093 | 0.0095 |
| sponsor_substitution | mnar_out | M2 | L1g | roc_auc | 30 | 0.5167 | 0.0104 |
| sponsor_substitution | mnar_out | M2 | L2 | pr_auc | 30 | 0.5105 | 0.0059 |
| sponsor_substitution | mnar_out | M2 | L2 | precision_at_k | 30 | 0.5060 | 0.0051 |
| sponsor_substitution | mnar_out | M2 | L2 | recall_at_k | 30 | 0.5060 | 0.0051 |
| sponsor_substitution | mnar_out | M2 | L2 | roc_auc | 30 | 0.5073 | 0.0042 |
| sponsor_substitution | mnar_out | M3 | L1 | pr_auc | 30 | 0.4938 | 0.0119 |
| sponsor_substitution | mnar_out | M3 | L1 | precision_at_k | 30 | 0.5067 | 0.0085 |
| sponsor_substitution | mnar_out | M3 | L1 | recall_at_k | 30 | 0.5067 | 0.0085 |
| sponsor_substitution | mnar_out | M3 | L1 | roc_auc | 30 | 0.4990 | 0.0124 |
| sponsor_substitution | mnar_out | M3 | L1g | pr_auc | 30 | 0.4938 | 0.0119 |
| sponsor_substitution | mnar_out | M3 | L1g | precision_at_k | 30 | 0.5070 | 0.0086 |
| sponsor_substitution | mnar_out | M3 | L1g | recall_at_k | 30 | 0.5070 | 0.0086 |
| sponsor_substitution | mnar_out | M3 | L1g | roc_auc | 30 | 0.4991 | 0.0123 |
| sponsor_substitution | mnar_out | M3 | L2 | pr_auc | 30 | 0.4932 | 0.0075 |
| sponsor_substitution | mnar_out | M3 | L2 | precision_at_k | 30 | 0.5050 | 0.0050 |
| sponsor_substitution | mnar_out | M3 | L2 | recall_at_k | 30 | 0.5050 | 0.0050 |
| sponsor_substitution | mnar_out | M3 | L2 | roc_auc | 30 | 0.5002 | 0.0051 |
| sponsor_substitution | mnar_out | M4 | L1 | pr_auc | 30 | 0.4965 | 0.0112 |
| sponsor_substitution | mnar_out | M4 | L1 | precision_at_k | 30 | 0.5073 | 0.0089 |
| sponsor_substitution | mnar_out | M4 | L1 | recall_at_k | 30 | 0.5073 | 0.0089 |
| sponsor_substitution | mnar_out | M4 | L1 | roc_auc | 30 | 0.5028 | 0.0115 |
| sponsor_substitution | mnar_out | M4 | L1g | pr_auc | 30 | 0.4965 | 0.0112 |
| sponsor_substitution | mnar_out | M4 | L1g | precision_at_k | 30 | 0.5070 | 0.0085 |
| sponsor_substitution | mnar_out | M4 | L1g | recall_at_k | 30 | 0.5070 | 0.0085 |
| sponsor_substitution | mnar_out | M4 | L1g | roc_auc | 30 | 0.5029 | 0.0114 |
| sponsor_substitution | mnar_out | M4 | L2 | pr_auc | 30 | 0.4955 | 0.0067 |
| sponsor_substitution | mnar_out | M4 | L2 | precision_at_k | 30 | 0.5052 | 0.0053 |
| sponsor_substitution | mnar_out | M4 | L2 | recall_at_k | 30 | 0.5052 | 0.0053 |
| sponsor_substitution | mnar_out | M4 | L2 | roc_auc | 30 | 0.5016 | 0.0048 |
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

This L2 is a product of single-dyad conditional-pseudolikelihood scores, not the matched-marginal L2 used for the plan's dependence increment. No L3-F joint simulation, L3-C concept score, or native-event probability is reported here. Those require separate conditional simulation and target-specific analysis.

## Aggregate MPLE numerical diagnostics

No coefficient-inference claim is made. Models use MPLE without coefficient regularization or input standardization.
The table reports fitting and conditional-score stability only; no coefficient values are released.

| Model | fits attempted/scored | failures | fit/prediction warnings | nonfinite coefficients | max $|\hat\theta|$ | exact $p=0/1$ |
|---|---:|---:|---:|---:|---:|---:|
| M0 | 60/60 | 0 | 0/0 | 0 | 0.767 | 0/0 |
| M1 | 60/60 | 0 | 0/0 | 0 | 1.484 | 0/0 |
| M2 | 60/60 | 0 | 0/0 | 0 | 205.426 | 0/0 |
| M3 | 60/59 | 1 | 0/0 | 0 | 202.344 | 0/0 |
| M4 | 60/60 | 0 | 0/0 | 0 | 134.129 | 0/0 |
| M4c | 60/60 | 0 | 0/0 | 0 | 85.034 | 0/0 |
