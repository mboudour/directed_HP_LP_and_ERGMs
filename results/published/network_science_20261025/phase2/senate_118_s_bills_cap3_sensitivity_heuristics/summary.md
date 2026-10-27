# Event-first native-event heuristic benchmark

- Dataset: `senate_118_s_bills`
- Target: held-out native tail/head **event types**; duplicate records of a selected type were removed together before scoring.
- Candidate universe: participants are pairwise within weak distance two in the split's observed projection. Random negatives are matched exactly on tail/head arity and are not observed or held-out native event types.
- Scores are uncalibrated ranking rules. ROC-AUC, PR-AUC, precision@k, and recall@k are valid here; accuracy, F1, MCC, and log loss are intentionally omitted.

- Senate temporal rule: each synthetic negative is paired with one held-out positive event type and every participant must serve on every distinct associated Bill Status introduction date under half-open roster intervals.
## Candidate-panel coverage

| Mechanism | Replicate | Held-out types | Positive types eligible for the candidate universe | Random negatives |
|---|---:|---:|---:|---:|
| mcar | 1 | 672 | 670 | 670 |
| mcar | 2 | 672 | 669 | 669 |
| mcar | 3 | 672 | 671 | 671 |
| mcar | 4 | 672 | 670 | 670 |
| mcar | 5 | 672 | 669 | 669 |
| mcar | 6 | 672 | 669 | 669 |
| mcar | 7 | 672 | 668 | 668 |
| mcar | 8 | 672 | 672 | 672 |
| mcar | 9 | 672 | 670 | 670 |
| mcar | 10 | 672 | 670 | 670 |
| mcar | 11 | 672 | 669 | 669 |
| mcar | 12 | 672 | 671 | 671 |
| mcar | 13 | 672 | 670 | 670 |
| mcar | 14 | 672 | 672 | 672 |
| mcar | 15 | 672 | 667 | 667 |
| mcar | 16 | 672 | 672 | 672 |
| mcar | 17 | 672 | 667 | 667 |
| mcar | 18 | 672 | 671 | 671 |
| mcar | 19 | 672 | 669 | 669 |
| mcar | 20 | 672 | 670 | 670 |
| mcar | 21 | 672 | 669 | 669 |
| mcar | 22 | 672 | 671 | 671 |
| mcar | 23 | 672 | 670 | 670 |
| mcar | 24 | 672 | 671 | 671 |
| mcar | 25 | 672 | 669 | 669 |
| mcar | 26 | 672 | 672 | 672 |
| mcar | 27 | 672 | 671 | 671 |
| mcar | 28 | 672 | 671 | 671 |
| mcar | 29 | 672 | 671 | 671 |
| mcar | 30 | 672 | 669 | 669 |
| mnar_out | 1 | 661 | 658 | 658 |
| mnar_out | 2 | 706 | 702 | 702 |
| mnar_out | 3 | 649 | 648 | 648 |
| mnar_out | 4 | 674 | 672 | 672 |
| mnar_out | 5 | 671 | 670 | 670 |
| mnar_out | 6 | 700 | 698 | 698 |
| mnar_out | 7 | 686 | 685 | 685 |
| mnar_out | 8 | 687 | 686 | 686 |
| mnar_out | 9 | 677 | 676 | 676 |
| mnar_out | 10 | 710 | 707 | 707 |
| mnar_out | 11 | 658 | 656 | 656 |
| mnar_out | 12 | 677 | 676 | 676 |
| mnar_out | 13 | 693 | 692 | 692 |
| mnar_out | 14 | 668 | 667 | 667 |
| mnar_out | 15 | 678 | 677 | 677 |
| mnar_out | 16 | 696 | 694 | 694 |
| mnar_out | 17 | 660 | 658 | 658 |
| mnar_out | 18 | 691 | 688 | 688 |
| mnar_out | 19 | 670 | 669 | 669 |
| mnar_out | 20 | 675 | 674 | 674 |
| mnar_out | 21 | 672 | 671 | 671 |
| mnar_out | 22 | 698 | 697 | 697 |
| mnar_out | 23 | 661 | 660 | 660 |
| mnar_out | 24 | 663 | 662 | 662 |
| mnar_out | 25 | 650 | 649 | 649 |
| mnar_out | 26 | 657 | 654 | 654 |
| mnar_out | 27 | 679 | 677 | 677 |
| mnar_out | 28 | 661 | 660 | 660 |
| mnar_out | 29 | 656 | 654 | 654 |
| mnar_out | 30 | 685 | 684 | 684 |

## Ranking metrics across completed replicates

| Mechanism | Score | Metric | Completed replicates | Mean | SD |
|---|---|---|---:|---:|---:|
| mcar | already_observed_footprint | pr_auc | 30 | 0.5740 | 0.0081 |
| mcar | already_observed_footprint | precision_at_k | 30 | 0.5578 | 0.0058 |
| mcar | already_observed_footprint | recall_at_k | 30 | 0.5578 | 0.0058 |
| mcar | already_observed_footprint | roc_auc | 30 | 0.5954 | 0.0087 |
| mcar | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.6382 | 0.0154 |
| mcar | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.6189 | 0.0130 |
| mcar | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.6189 | 0.0130 |
| mcar | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.6607 | 0.0143 |
| mcar | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.6790 | 0.0130 |
| mcar | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.6348 | 0.0128 |
| mcar | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.6348 | 0.0128 |
| mcar | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.6849 | 0.0108 |
| mcar | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.6524 | 0.0154 |
| mcar | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.6083 | 0.0135 |
| mcar | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.6083 | 0.0135 |
| mcar | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.6526 | 0.0146 |
| mcar | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.6854 | 0.0135 |
| mcar | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.6388 | 0.0119 |
| mcar | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.6388 | 0.0119 |
| mcar | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.6936 | 0.0126 |
| mcar | lifted_cn_total_mean | pr_auc | 30 | 0.6810 | 0.0135 |
| mcar | lifted_cn_total_mean | precision_at_k | 30 | 0.6378 | 0.0118 |
| mcar | lifted_cn_total_mean | recall_at_k | 30 | 0.6378 | 0.0118 |
| mcar | lifted_cn_total_mean | roc_auc | 30 | 0.6923 | 0.0127 |
| mcar | lifted_degree_product_mean | pr_auc | 30 | 0.6798 | 0.0134 |
| mcar | lifted_degree_product_mean | precision_at_k | 30 | 0.6359 | 0.0095 |
| mcar | lifted_degree_product_mean | recall_at_k | 30 | 0.6359 | 0.0095 |
| mcar | lifted_degree_product_mean | roc_auc | 30 | 0.6880 | 0.0120 |
| mcar | lifted_ii_mean | pr_auc | 30 | 0.6309 | 0.0146 |
| mcar | lifted_ii_mean | precision_at_k | 30 | 0.6174 | 0.0123 |
| mcar | lifted_ii_mean | recall_at_k | 30 | 0.6174 | 0.0123 |
| mcar | lifted_ii_mean | roc_auc | 30 | 0.6592 | 0.0144 |
| mcar | lifted_oi_mean | pr_auc | 30 | 0.6700 | 0.0124 |
| mcar | lifted_oi_mean | precision_at_k | 30 | 0.6341 | 0.0124 |
| mcar | lifted_oi_mean | recall_at_k | 30 | 0.6341 | 0.0124 |
| mcar | lifted_oi_mean | roc_auc | 30 | 0.6838 | 0.0109 |
| mcar | lifted_oo_mean | pr_auc | 30 | 0.6427 | 0.0155 |
| mcar | lifted_oo_mean | precision_at_k | 30 | 0.6066 | 0.0137 |
| mcar | lifted_oo_mean | recall_at_k | 30 | 0.6066 | 0.0137 |
| mcar | lifted_oo_mean | roc_auc | 30 | 0.6501 | 0.0147 |
| mcar | lifted_reverse_arc_mean | pr_auc | 30 | 0.6261 | 0.0127 |
| mcar | lifted_reverse_arc_mean | precision_at_k | 30 | 0.6211 | 0.0100 |
| mcar | lifted_reverse_arc_mean | recall_at_k | 30 | 0.6211 | 0.0100 |
| mcar | lifted_reverse_arc_mean | roc_auc | 30 | 0.6579 | 0.0119 |
| mnar_out | already_observed_footprint | pr_auc | 30 | 0.5725 | 0.0084 |
| mnar_out | already_observed_footprint | precision_at_k | 30 | 0.5551 | 0.0053 |
| mnar_out | already_observed_footprint | recall_at_k | 30 | 0.5551 | 0.0053 |
| mnar_out | already_observed_footprint | roc_auc | 30 | 0.5922 | 0.0084 |
| mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.6828 | 0.0167 |
| mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.6542 | 0.0120 |
| mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.6542 | 0.0120 |
| mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.7075 | 0.0140 |
| mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.6895 | 0.0176 |
| mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.6460 | 0.0168 |
| mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.6460 | 0.0168 |
| mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.6998 | 0.0187 |
| mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.6527 | 0.0213 |
| mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.6138 | 0.0195 |
| mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.6138 | 0.0195 |
| mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.6604 | 0.0240 |
| mnar_out | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.7115 | 0.0183 |
| mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.6680 | 0.0150 |
| mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.6680 | 0.0150 |
| mnar_out | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.7312 | 0.0157 |
| mnar_out | lifted_cn_total_mean | pr_auc | 30 | 0.7058 | 0.0183 |
| mnar_out | lifted_cn_total_mean | precision_at_k | 30 | 0.6670 | 0.0148 |
| mnar_out | lifted_cn_total_mean | recall_at_k | 30 | 0.6670 | 0.0148 |
| mnar_out | lifted_cn_total_mean | roc_auc | 30 | 0.7297 | 0.0159 |
| mnar_out | lifted_degree_product_mean | pr_auc | 30 | 0.6900 | 0.0174 |
| mnar_out | lifted_degree_product_mean | precision_at_k | 30 | 0.6433 | 0.0146 |
| mnar_out | lifted_degree_product_mean | recall_at_k | 30 | 0.6433 | 0.0146 |
| mnar_out | lifted_degree_product_mean | roc_auc | 30 | 0.6999 | 0.0216 |
| mnar_out | lifted_ii_mean | pr_auc | 30 | 0.6755 | 0.0158 |
| mnar_out | lifted_ii_mean | precision_at_k | 30 | 0.6538 | 0.0119 |
| mnar_out | lifted_ii_mean | recall_at_k | 30 | 0.6538 | 0.0119 |
| mnar_out | lifted_ii_mean | roc_auc | 30 | 0.7074 | 0.0140 |
| mnar_out | lifted_oi_mean | pr_auc | 30 | 0.6795 | 0.0167 |
| mnar_out | lifted_oi_mean | precision_at_k | 30 | 0.6471 | 0.0170 |
| mnar_out | lifted_oi_mean | recall_at_k | 30 | 0.6471 | 0.0170 |
| mnar_out | lifted_oi_mean | roc_auc | 30 | 0.6988 | 0.0184 |
| mnar_out | lifted_oo_mean | pr_auc | 30 | 0.6394 | 0.0208 |
| mnar_out | lifted_oo_mean | precision_at_k | 30 | 0.6113 | 0.0203 |
| mnar_out | lifted_oo_mean | recall_at_k | 30 | 0.6113 | 0.0203 |
| mnar_out | lifted_oo_mean | roc_auc | 30 | 0.6574 | 0.0240 |
| mnar_out | lifted_reverse_arc_mean | pr_auc | 30 | 0.6443 | 0.0120 |
| mnar_out | lifted_reverse_arc_mean | precision_at_k | 30 | 0.6397 | 0.0088 |
| mnar_out | lifted_reverse_arc_mean | recall_at_k | 30 | 0.6397 | 0.0088 |
| mnar_out | lifted_reverse_arc_mean | roc_auc | 30 | 0.6769 | 0.0104 |

The `already_observed_footprint` score is a baseline, not a predictor: it indicates that an observed event type already induces every arc of the held-out candidate's footprint. A high value demonstrates event non-identifiability from the observed dyads.
