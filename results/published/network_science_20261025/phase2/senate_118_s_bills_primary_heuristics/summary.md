# Event-first native-event heuristic benchmark

- Dataset: `senate_118_s_bills`
- Target: held-out native tail/head **event types**; duplicate records of a selected type were removed together before scoring.
- Candidate universe: participants are pairwise within weak distance two in the split's observed projection. Random negatives are matched exactly on tail/head arity and are not observed or held-out native event types.
- Scores are uncalibrated ranking rules. ROC-AUC, PR-AUC, precision@k, and recall@k are valid here; accuracy, F1, MCC, and log loss are intentionally omitted.

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
| mcar | already_observed_footprint | pr_auc | 30 | 0.6086 | 0.0097 |
| mcar | already_observed_footprint | precision_at_k | 30 | 0.6006 | 0.0079 |
| mcar | already_observed_footprint | recall_at_k | 30 | 0.6006 | 0.0079 |
| mcar | already_observed_footprint | roc_auc | 30 | 0.6440 | 0.0102 |
| mcar | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.7037 | 0.0116 |
| mcar | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.6562 | 0.0101 |
| mcar | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.6562 | 0.0101 |
| mcar | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.7162 | 0.0100 |
| mcar | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.7355 | 0.0124 |
| mcar | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.6721 | 0.0107 |
| mcar | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.6721 | 0.0107 |
| mcar | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.7373 | 0.0106 |
| mcar | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.7038 | 0.0119 |
| mcar | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.6482 | 0.0088 |
| mcar | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.6482 | 0.0088 |
| mcar | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.7047 | 0.0086 |
| mcar | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.7425 | 0.0122 |
| mcar | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.6779 | 0.0097 |
| mcar | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.6779 | 0.0097 |
| mcar | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.7425 | 0.0097 |
| mcar | lifted_cn_total_mean | pr_auc | 30 | 0.7402 | 0.0124 |
| mcar | lifted_cn_total_mean | precision_at_k | 30 | 0.6769 | 0.0100 |
| mcar | lifted_cn_total_mean | recall_at_k | 30 | 0.6769 | 0.0100 |
| mcar | lifted_cn_total_mean | roc_auc | 30 | 0.7418 | 0.0099 |
| mcar | lifted_degree_product_mean | pr_auc | 30 | 0.6973 | 0.0125 |
| mcar | lifted_degree_product_mean | precision_at_k | 30 | 0.6482 | 0.0092 |
| mcar | lifted_degree_product_mean | recall_at_k | 30 | 0.6482 | 0.0092 |
| mcar | lifted_degree_product_mean | roc_auc | 30 | 0.7071 | 0.0099 |
| mcar | lifted_ii_mean | pr_auc | 30 | 0.6987 | 0.0116 |
| mcar | lifted_ii_mean | precision_at_k | 30 | 0.6541 | 0.0104 |
| mcar | lifted_ii_mean | recall_at_k | 30 | 0.6541 | 0.0104 |
| mcar | lifted_ii_mean | roc_auc | 30 | 0.7143 | 0.0102 |
| mcar | lifted_oi_mean | pr_auc | 30 | 0.7317 | 0.0125 |
| mcar | lifted_oi_mean | precision_at_k | 30 | 0.6709 | 0.0103 |
| mcar | lifted_oi_mean | recall_at_k | 30 | 0.6709 | 0.0103 |
| mcar | lifted_oi_mean | roc_auc | 30 | 0.7364 | 0.0107 |
| mcar | lifted_oo_mean | pr_auc | 30 | 0.6992 | 0.0120 |
| mcar | lifted_oo_mean | precision_at_k | 30 | 0.6474 | 0.0092 |
| mcar | lifted_oo_mean | recall_at_k | 30 | 0.6474 | 0.0092 |
| mcar | lifted_oo_mean | roc_auc | 30 | 0.7034 | 0.0086 |
| mcar | lifted_reverse_arc_mean | pr_auc | 30 | 0.6654 | 0.0084 |
| mcar | lifted_reverse_arc_mean | precision_at_k | 30 | 0.6773 | 0.0073 |
| mcar | lifted_reverse_arc_mean | recall_at_k | 30 | 0.6773 | 0.0073 |
| mcar | lifted_reverse_arc_mean | roc_auc | 30 | 0.7008 | 0.0076 |
| mnar_out | already_observed_footprint | pr_auc | 30 | 0.6205 | 0.0099 |
| mnar_out | already_observed_footprint | precision_at_k | 30 | 0.6101 | 0.0074 |
| mnar_out | already_observed_footprint | recall_at_k | 30 | 0.6101 | 0.0074 |
| mnar_out | already_observed_footprint | roc_auc | 30 | 0.6563 | 0.0098 |
| mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.7534 | 0.0116 |
| mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.7040 | 0.0108 |
| mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.7040 | 0.0108 |
| mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.7704 | 0.0107 |
| mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.7802 | 0.0168 |
| mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.7328 | 0.0131 |
| mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.7328 | 0.0131 |
| mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.8011 | 0.0127 |
| mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.7380 | 0.0181 |
| mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.7029 | 0.0125 |
| mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.7029 | 0.0125 |
| mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.7667 | 0.0144 |
| mnar_out | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.7931 | 0.0136 |
| mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.7414 | 0.0115 |
| mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.7414 | 0.0115 |
| mnar_out | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.8108 | 0.0104 |
| mnar_out | lifted_cn_total_mean | pr_auc | 30 | 0.7910 | 0.0139 |
| mnar_out | lifted_cn_total_mean | precision_at_k | 30 | 0.7411 | 0.0117 |
| mnar_out | lifted_cn_total_mean | recall_at_k | 30 | 0.7411 | 0.0117 |
| mnar_out | lifted_cn_total_mean | roc_auc | 30 | 0.8105 | 0.0106 |
| mnar_out | lifted_degree_product_mean | pr_auc | 30 | 0.7250 | 0.0145 |
| mnar_out | lifted_degree_product_mean | precision_at_k | 30 | 0.6881 | 0.0131 |
| mnar_out | lifted_degree_product_mean | recall_at_k | 30 | 0.6881 | 0.0131 |
| mnar_out | lifted_degree_product_mean | roc_auc | 30 | 0.7544 | 0.0140 |
| mnar_out | lifted_ii_mean | pr_auc | 30 | 0.7496 | 0.0116 |
| mnar_out | lifted_ii_mean | precision_at_k | 30 | 0.7022 | 0.0107 |
| mnar_out | lifted_ii_mean | recall_at_k | 30 | 0.7022 | 0.0107 |
| mnar_out | lifted_ii_mean | roc_auc | 30 | 0.7687 | 0.0108 |
| mnar_out | lifted_oi_mean | pr_auc | 30 | 0.7763 | 0.0167 |
| mnar_out | lifted_oi_mean | precision_at_k | 30 | 0.7324 | 0.0133 |
| mnar_out | lifted_oi_mean | recall_at_k | 30 | 0.7324 | 0.0133 |
| mnar_out | lifted_oi_mean | roc_auc | 30 | 0.8005 | 0.0127 |
| mnar_out | lifted_oo_mean | pr_auc | 30 | 0.7322 | 0.0185 |
| mnar_out | lifted_oo_mean | precision_at_k | 30 | 0.7013 | 0.0121 |
| mnar_out | lifted_oo_mean | recall_at_k | 30 | 0.7013 | 0.0121 |
| mnar_out | lifted_oo_mean | roc_auc | 30 | 0.7648 | 0.0146 |
| mnar_out | lifted_reverse_arc_mean | pr_auc | 30 | 0.6917 | 0.0142 |
| mnar_out | lifted_reverse_arc_mean | precision_at_k | 30 | 0.7026 | 0.0097 |
| mnar_out | lifted_reverse_arc_mean | recall_at_k | 30 | 0.7026 | 0.0097 |
| mnar_out | lifted_reverse_arc_mean | roc_auc | 30 | 0.7306 | 0.0127 |

The `already_observed_footprint` score is a baseline, not a predictor: it indicates that an observed event type already induces every arc of the held-out candidate's footprint. A high value demonstrates event non-identifiability from the observed dyads.
