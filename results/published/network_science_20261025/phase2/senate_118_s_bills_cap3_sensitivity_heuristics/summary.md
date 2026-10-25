# Event-first native-event heuristic benchmark

- Dataset: `senate_118_s_bills_cap3_sensitivity`
- Target: held-out native tail/head **event types**; duplicate records of a selected type were removed together before scoring.
- Candidate universe: participants are pairwise within weak distance two in the split's observed projection. Random negatives are matched exactly on tail/head arity and are not observed or held-out native event types.
- Scores are uncalibrated ranking rules. ROC-AUC, PR-AUC, precision@k, and recall@k are valid here; accuracy, F1, MCC, and log loss are intentionally omitted.

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
| mcar | already_observed_footprint | pr_auc | 30 | 0.5789 | 0.0098 |
| mcar | already_observed_footprint | precision_at_k | 30 | 0.5600 | 0.0064 |
| mcar | already_observed_footprint | recall_at_k | 30 | 0.5600 | 0.0064 |
| mcar | already_observed_footprint | roc_auc | 30 | 0.5994 | 0.0099 |
| mcar | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.6493 | 0.0190 |
| mcar | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.6269 | 0.0141 |
| mcar | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.6269 | 0.0141 |
| mcar | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.6720 | 0.0153 |
| mcar | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.6866 | 0.0130 |
| mcar | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.6411 | 0.0097 |
| mcar | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.6411 | 0.0097 |
| mcar | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.6940 | 0.0093 |
| mcar | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.6636 | 0.0155 |
| mcar | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.6150 | 0.0135 |
| mcar | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.6150 | 0.0135 |
| mcar | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.6630 | 0.0139 |
| mcar | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.6968 | 0.0156 |
| mcar | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.6462 | 0.0106 |
| mcar | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.6462 | 0.0106 |
| mcar | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.7048 | 0.0127 |
| mcar | lifted_cn_total_mean | pr_auc | 30 | 0.6922 | 0.0153 |
| mcar | lifted_cn_total_mean | precision_at_k | 30 | 0.6453 | 0.0109 |
| mcar | lifted_cn_total_mean | recall_at_k | 30 | 0.6453 | 0.0109 |
| mcar | lifted_cn_total_mean | roc_auc | 30 | 0.7035 | 0.0126 |
| mcar | lifted_degree_product_mean | pr_auc | 30 | 0.6896 | 0.0147 |
| mcar | lifted_degree_product_mean | precision_at_k | 30 | 0.6464 | 0.0088 |
| mcar | lifted_degree_product_mean | recall_at_k | 30 | 0.6464 | 0.0088 |
| mcar | lifted_degree_product_mean | roc_auc | 30 | 0.7001 | 0.0113 |
| mcar | lifted_ii_mean | pr_auc | 30 | 0.6421 | 0.0182 |
| mcar | lifted_ii_mean | precision_at_k | 30 | 0.6262 | 0.0132 |
| mcar | lifted_ii_mean | recall_at_k | 30 | 0.6262 | 0.0132 |
| mcar | lifted_ii_mean | roc_auc | 30 | 0.6705 | 0.0152 |
| mcar | lifted_oi_mean | pr_auc | 30 | 0.6779 | 0.0123 |
| mcar | lifted_oi_mean | precision_at_k | 30 | 0.6400 | 0.0098 |
| mcar | lifted_oi_mean | recall_at_k | 30 | 0.6400 | 0.0098 |
| mcar | lifted_oi_mean | roc_auc | 30 | 0.6927 | 0.0096 |
| mcar | lifted_oo_mean | pr_auc | 30 | 0.6533 | 0.0153 |
| mcar | lifted_oo_mean | precision_at_k | 30 | 0.6135 | 0.0128 |
| mcar | lifted_oo_mean | recall_at_k | 30 | 0.6135 | 0.0128 |
| mcar | lifted_oo_mean | roc_auc | 30 | 0.6603 | 0.0142 |
| mcar | lifted_reverse_arc_mean | pr_auc | 30 | 0.6340 | 0.0114 |
| mcar | lifted_reverse_arc_mean | precision_at_k | 30 | 0.6248 | 0.0094 |
| mcar | lifted_reverse_arc_mean | recall_at_k | 30 | 0.6248 | 0.0094 |
| mcar | lifted_reverse_arc_mean | roc_auc | 30 | 0.6644 | 0.0111 |
| mnar_out | already_observed_footprint | pr_auc | 30 | 0.5716 | 0.0085 |
| mnar_out | already_observed_footprint | precision_at_k | 30 | 0.5547 | 0.0054 |
| mnar_out | already_observed_footprint | recall_at_k | 30 | 0.5547 | 0.0054 |
| mnar_out | already_observed_footprint | roc_auc | 30 | 0.5915 | 0.0085 |
| mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.6934 | 0.0175 |
| mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.6628 | 0.0123 |
| mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.6628 | 0.0123 |
| mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.7180 | 0.0141 |
| mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.6967 | 0.0184 |
| mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.6533 | 0.0206 |
| mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.6533 | 0.0206 |
| mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.7076 | 0.0211 |
| mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.6572 | 0.0191 |
| mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.6190 | 0.0220 |
| mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.6190 | 0.0220 |
| mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.6670 | 0.0238 |
| mnar_out | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.7206 | 0.0199 |
| mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.6740 | 0.0171 |
| mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.6740 | 0.0171 |
| mnar_out | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.7398 | 0.0169 |
| mnar_out | lifted_cn_total_mean | pr_auc | 30 | 0.7145 | 0.0198 |
| mnar_out | lifted_cn_total_mean | precision_at_k | 30 | 0.6730 | 0.0173 |
| mnar_out | lifted_cn_total_mean | recall_at_k | 30 | 0.6730 | 0.0173 |
| mnar_out | lifted_cn_total_mean | roc_auc | 30 | 0.7381 | 0.0174 |
| mnar_out | lifted_degree_product_mean | pr_auc | 30 | 0.6984 | 0.0179 |
| mnar_out | lifted_degree_product_mean | precision_at_k | 30 | 0.6488 | 0.0168 |
| mnar_out | lifted_degree_product_mean | recall_at_k | 30 | 0.6488 | 0.0168 |
| mnar_out | lifted_degree_product_mean | roc_auc | 30 | 0.7087 | 0.0225 |
| mnar_out | lifted_ii_mean | pr_auc | 30 | 0.6859 | 0.0170 |
| mnar_out | lifted_ii_mean | precision_at_k | 30 | 0.6622 | 0.0118 |
| mnar_out | lifted_ii_mean | recall_at_k | 30 | 0.6622 | 0.0118 |
| mnar_out | lifted_ii_mean | roc_auc | 30 | 0.7177 | 0.0142 |
| mnar_out | lifted_oi_mean | pr_auc | 30 | 0.6866 | 0.0174 |
| mnar_out | lifted_oi_mean | precision_at_k | 30 | 0.6531 | 0.0209 |
| mnar_out | lifted_oi_mean | recall_at_k | 30 | 0.6531 | 0.0209 |
| mnar_out | lifted_oi_mean | roc_auc | 30 | 0.7064 | 0.0210 |
| mnar_out | lifted_oo_mean | pr_auc | 30 | 0.6436 | 0.0182 |
| mnar_out | lifted_oo_mean | precision_at_k | 30 | 0.6163 | 0.0217 |
| mnar_out | lifted_oo_mean | recall_at_k | 30 | 0.6163 | 0.0217 |
| mnar_out | lifted_oo_mean | roc_auc | 30 | 0.6640 | 0.0237 |
| mnar_out | lifted_reverse_arc_mean | pr_auc | 30 | 0.6502 | 0.0101 |
| mnar_out | lifted_reverse_arc_mean | precision_at_k | 30 | 0.6428 | 0.0079 |
| mnar_out | lifted_reverse_arc_mean | recall_at_k | 30 | 0.6428 | 0.0079 |
| mnar_out | lifted_reverse_arc_mean | roc_auc | 30 | 0.6821 | 0.0089 |

The `already_observed_footprint` score is a baseline, not a predictor: it indicates that an observed event type already induces every arc of the held-out candidate's footprint. A high value demonstrates event non-identifiability from the observed dyads.
