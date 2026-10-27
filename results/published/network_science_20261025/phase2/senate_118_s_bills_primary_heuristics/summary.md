# Event-first native-event heuristic benchmark

- Dataset: `senate_118_s_bills`
- Target: held-out native tail/head **event types**; duplicate records of a selected type were removed together before scoring.
- Candidate universe: participants are pairwise within weak distance two in the split's observed projection. Random negatives are matched exactly on tail/head arity and are not observed or held-out native event types.
- Scores are uncalibrated ranking rules. ROC-AUC, PR-AUC, precision@k, and recall@k are valid here; accuracy, F1, MCC, and log loss are intentionally omitted.

- Senate temporal rule: each synthetic negative is paired with one held-out positive event type and every participant must serve on every distinct associated Bill Status introduction date under half-open roster intervals.
## Candidate-panel coverage

| Mechanism | Replicate | Held-out types | Positive types eligible for the candidate universe | Random negatives |
|---|---:|---:|---:|---:|
| mcar | 1 | 962 | 962 | 962 |
| mcar | 2 | 962 | 961 | 961 |
| mcar | 3 | 962 | 961 | 961 |
| mcar | 4 | 962 | 962 | 962 |
| mcar | 5 | 962 | 962 | 962 |
| mcar | 6 | 962 | 962 | 962 |
| mcar | 7 | 962 | 961 | 961 |
| mcar | 8 | 962 | 960 | 960 |
| mcar | 9 | 962 | 961 | 961 |
| mcar | 10 | 962 | 961 | 961 |
| mcar | 11 | 962 | 962 | 962 |
| mcar | 12 | 962 | 962 | 962 |
| mcar | 13 | 962 | 962 | 962 |
| mcar | 14 | 962 | 962 | 962 |
| mcar | 15 | 962 | 962 | 962 |
| mcar | 16 | 962 | 961 | 961 |
| mcar | 17 | 962 | 962 | 962 |
| mcar | 18 | 962 | 962 | 962 |
| mcar | 19 | 962 | 962 | 962 |
| mcar | 20 | 962 | 962 | 962 |
| mcar | 21 | 962 | 961 | 961 |
| mcar | 22 | 962 | 962 | 962 |
| mcar | 23 | 962 | 960 | 960 |
| mcar | 24 | 962 | 962 | 962 |
| mcar | 25 | 962 | 962 | 962 |
| mcar | 26 | 962 | 962 | 962 |
| mcar | 27 | 962 | 960 | 960 |
| mcar | 28 | 962 | 962 | 962 |
| mcar | 29 | 962 | 959 | 959 |
| mcar | 30 | 962 | 962 | 962 |
| mnar_out | 1 | 946 | 946 | 946 |
| mnar_out | 2 | 972 | 972 | 972 |
| mnar_out | 3 | 962 | 962 | 962 |
| mnar_out | 4 | 965 | 964 | 964 |
| mnar_out | 5 | 925 | 925 | 925 |
| mnar_out | 6 | 1024 | 1024 | 1024 |
| mnar_out | 7 | 952 | 952 | 952 |
| mnar_out | 8 | 975 | 975 | 975 |
| mnar_out | 9 | 972 | 972 | 972 |
| mnar_out | 10 | 993 | 993 | 993 |
| mnar_out | 11 | 936 | 935 | 935 |
| mnar_out | 12 | 982 | 982 | 982 |
| mnar_out | 13 | 982 | 982 | 982 |
| mnar_out | 14 | 924 | 924 | 924 |
| mnar_out | 15 | 955 | 955 | 955 |
| mnar_out | 16 | 985 | 984 | 984 |
| mnar_out | 17 | 967 | 967 | 967 |
| mnar_out | 18 | 993 | 992 | 992 |
| mnar_out | 19 | 964 | 964 | 964 |
| mnar_out | 20 | 985 | 985 | 985 |
| mnar_out | 21 | 989 | 989 | 989 |
| mnar_out | 22 | 967 | 967 | 967 |
| mnar_out | 23 | 947 | 947 | 947 |
| mnar_out | 24 | 963 | 962 | 962 |
| mnar_out | 25 | 952 | 952 | 952 |
| mnar_out | 26 | 959 | 959 | 959 |
| mnar_out | 27 | 958 | 958 | 958 |
| mnar_out | 28 | 930 | 930 | 930 |
| mnar_out | 29 | 938 | 938 | 938 |
| mnar_out | 30 | 1001 | 1000 | 1000 |

## Ranking metrics across completed replicates

| Mechanism | Score | Metric | Completed replicates | Mean | SD |
|---|---|---|---:|---:|---:|
| mcar | already_observed_footprint | pr_auc | 30 | 0.6038 | 0.0073 |
| mcar | already_observed_footprint | precision_at_k | 30 | 0.5983 | 0.0068 |
| mcar | already_observed_footprint | recall_at_k | 30 | 0.5983 | 0.0068 |
| mcar | already_observed_footprint | roc_auc | 30 | 0.6397 | 0.0082 |
| mcar | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.6927 | 0.0130 |
| mcar | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.6495 | 0.0089 |
| mcar | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.6495 | 0.0089 |
| mcar | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.7039 | 0.0108 |
| mcar | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.7260 | 0.0114 |
| mcar | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.6637 | 0.0102 |
| mcar | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.6637 | 0.0102 |
| mcar | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.7269 | 0.0095 |
| mcar | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.6906 | 0.0126 |
| mcar | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.6399 | 0.0082 |
| mcar | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.6399 | 0.0082 |
| mcar | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.6942 | 0.0080 |
| mcar | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.7308 | 0.0105 |
| mcar | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.6707 | 0.0095 |
| mcar | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.6707 | 0.0095 |
| mcar | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.7313 | 0.0087 |
| mcar | lifted_cn_total_mean | pr_auc | 30 | 0.7283 | 0.0106 |
| mcar | lifted_cn_total_mean | precision_at_k | 30 | 0.6699 | 0.0097 |
| mcar | lifted_cn_total_mean | recall_at_k | 30 | 0.6699 | 0.0097 |
| mcar | lifted_cn_total_mean | roc_auc | 30 | 0.7306 | 0.0088 |
| mcar | lifted_degree_product_mean | pr_auc | 30 | 0.6868 | 0.0121 |
| mcar | lifted_degree_product_mean | precision_at_k | 30 | 0.6407 | 0.0085 |
| mcar | lifted_degree_product_mean | recall_at_k | 30 | 0.6407 | 0.0085 |
| mcar | lifted_degree_product_mean | roc_auc | 30 | 0.6957 | 0.0096 |
| mcar | lifted_ii_mean | pr_auc | 30 | 0.6877 | 0.0129 |
| mcar | lifted_ii_mean | precision_at_k | 30 | 0.6479 | 0.0084 |
| mcar | lifted_ii_mean | recall_at_k | 30 | 0.6479 | 0.0084 |
| mcar | lifted_ii_mean | roc_auc | 30 | 0.7020 | 0.0108 |
| mcar | lifted_oi_mean | pr_auc | 30 | 0.7220 | 0.0115 |
| mcar | lifted_oi_mean | precision_at_k | 30 | 0.6632 | 0.0103 |
| mcar | lifted_oi_mean | recall_at_k | 30 | 0.6632 | 0.0103 |
| mcar | lifted_oi_mean | roc_auc | 30 | 0.7261 | 0.0096 |
| mcar | lifted_oo_mean | pr_auc | 30 | 0.6859 | 0.0126 |
| mcar | lifted_oo_mean | precision_at_k | 30 | 0.6397 | 0.0086 |
| mcar | lifted_oo_mean | recall_at_k | 30 | 0.6397 | 0.0086 |
| mcar | lifted_oo_mean | roc_auc | 30 | 0.6928 | 0.0080 |
| mcar | lifted_reverse_arc_mean | pr_auc | 30 | 0.6565 | 0.0094 |
| mcar | lifted_reverse_arc_mean | precision_at_k | 30 | 0.6723 | 0.0081 |
| mcar | lifted_reverse_arc_mean | recall_at_k | 30 | 0.6723 | 0.0081 |
| mcar | lifted_reverse_arc_mean | roc_auc | 30 | 0.6928 | 0.0089 |
| mnar_out | already_observed_footprint | pr_auc | 30 | 0.6188 | 0.0082 |
| mnar_out | already_observed_footprint | precision_at_k | 30 | 0.6093 | 0.0066 |
| mnar_out | already_observed_footprint | recall_at_k | 30 | 0.6093 | 0.0066 |
| mnar_out | already_observed_footprint | roc_auc | 30 | 0.6549 | 0.0083 |
| mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.7483 | 0.0139 |
| mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.6979 | 0.0089 |
| mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.6979 | 0.0089 |
| mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.7626 | 0.0081 |
| mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.7744 | 0.0146 |
| mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.7276 | 0.0144 |
| mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.7276 | 0.0144 |
| mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.7954 | 0.0139 |
| mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.7338 | 0.0198 |
| mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.6986 | 0.0143 |
| mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.6986 | 0.0143 |
| mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.7603 | 0.0163 |
| mnar_out | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.7882 | 0.0144 |
| mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.7367 | 0.0117 |
| mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.7367 | 0.0117 |
| mnar_out | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.8045 | 0.0113 |
| mnar_out | lifted_cn_total_mean | pr_auc | 30 | 0.7861 | 0.0145 |
| mnar_out | lifted_cn_total_mean | precision_at_k | 30 | 0.7363 | 0.0118 |
| mnar_out | lifted_cn_total_mean | recall_at_k | 30 | 0.7363 | 0.0118 |
| mnar_out | lifted_cn_total_mean | roc_auc | 30 | 0.8042 | 0.0116 |
| mnar_out | lifted_degree_product_mean | pr_auc | 30 | 0.7180 | 0.0172 |
| mnar_out | lifted_degree_product_mean | precision_at_k | 30 | 0.6818 | 0.0166 |
| mnar_out | lifted_degree_product_mean | recall_at_k | 30 | 0.6818 | 0.0166 |
| mnar_out | lifted_degree_product_mean | roc_auc | 30 | 0.7468 | 0.0170 |
| mnar_out | lifted_ii_mean | pr_auc | 30 | 0.7442 | 0.0138 |
| mnar_out | lifted_ii_mean | precision_at_k | 30 | 0.6962 | 0.0087 |
| mnar_out | lifted_ii_mean | recall_at_k | 30 | 0.6962 | 0.0087 |
| mnar_out | lifted_ii_mean | roc_auc | 30 | 0.7609 | 0.0082 |
| mnar_out | lifted_oi_mean | pr_auc | 30 | 0.7707 | 0.0145 |
| mnar_out | lifted_oi_mean | precision_at_k | 30 | 0.7269 | 0.0144 |
| mnar_out | lifted_oi_mean | recall_at_k | 30 | 0.7269 | 0.0144 |
| mnar_out | lifted_oi_mean | roc_auc | 30 | 0.7948 | 0.0138 |
| mnar_out | lifted_oo_mean | pr_auc | 30 | 0.7282 | 0.0198 |
| mnar_out | lifted_oo_mean | precision_at_k | 30 | 0.6977 | 0.0140 |
| mnar_out | lifted_oo_mean | recall_at_k | 30 | 0.6977 | 0.0140 |
| mnar_out | lifted_oo_mean | roc_auc | 30 | 0.7586 | 0.0165 |
| mnar_out | lifted_reverse_arc_mean | pr_auc | 30 | 0.6868 | 0.0114 |
| mnar_out | lifted_reverse_arc_mean | precision_at_k | 30 | 0.6984 | 0.0094 |
| mnar_out | lifted_reverse_arc_mean | recall_at_k | 30 | 0.6984 | 0.0094 |
| mnar_out | lifted_reverse_arc_mean | roc_auc | 30 | 0.7258 | 0.0107 |

The `already_observed_footprint` score is a baseline, not a predictor: it indicates that an observed event type already induces every arc of the held-out candidate's footprint. A high value demonstrates event non-identifiability from the observed dyads.
