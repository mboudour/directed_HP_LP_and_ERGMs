# Senate sponsor-substitution hard-negative benchmark

- Dataset: `senate_118_s_bills_cap3_sensitivity`
- Each pair retains one sponsor and the same bill participants by exchanging the sponsor with one original co-sponsor.
- Reversal/orientation is absent because it would turn a 1-to-h bill into h-to-1 roles.

## Coverage

| Mechanism | Replicate | Eligible held-out types | Sponsor-substitution pairs |
|---|---:|---:|---:|
| mcar | 1 | 670 | 516 |
| mcar | 2 | 669 | 533 |
| mcar | 3 | 671 | 519 |
| mcar | 4 | 670 | 533 |
| mcar | 5 | 669 | 537 |
| mcar | 6 | 669 | 527 |
| mcar | 7 | 668 | 520 |
| mcar | 8 | 672 | 538 |
| mcar | 9 | 670 | 525 |
| mcar | 10 | 670 | 544 |
| mcar | 11 | 669 | 539 |
| mcar | 12 | 671 | 528 |
| mcar | 13 | 670 | 534 |
| mcar | 14 | 672 | 544 |
| mcar | 15 | 667 | 543 |
| mcar | 16 | 672 | 540 |
| mcar | 17 | 667 | 540 |
| mcar | 18 | 671 | 526 |
| mcar | 19 | 669 | 543 |
| mcar | 20 | 670 | 535 |
| mcar | 21 | 669 | 543 |
| mcar | 22 | 671 | 523 |
| mcar | 23 | 670 | 536 |
| mcar | 24 | 671 | 550 |
| mcar | 25 | 669 | 515 |
| mcar | 26 | 672 | 542 |
| mcar | 27 | 671 | 531 |
| mcar | 28 | 671 | 528 |
| mcar | 29 | 671 | 534 |
| mcar | 30 | 669 | 532 |
| mnar_out | 1 | 658 | 525 |
| mnar_out | 2 | 702 | 565 |
| mnar_out | 3 | 648 | 532 |
| mnar_out | 4 | 672 | 547 |
| mnar_out | 5 | 670 | 528 |
| mnar_out | 6 | 698 | 550 |
| mnar_out | 7 | 685 | 544 |
| mnar_out | 8 | 686 | 554 |
| mnar_out | 9 | 676 | 546 |
| mnar_out | 10 | 707 | 562 |
| mnar_out | 11 | 656 | 532 |
| mnar_out | 12 | 676 | 537 |
| mnar_out | 13 | 692 | 559 |
| mnar_out | 14 | 667 | 526 |
| mnar_out | 15 | 677 | 539 |
| mnar_out | 16 | 694 | 556 |
| mnar_out | 17 | 658 | 517 |
| mnar_out | 18 | 688 | 545 |
| mnar_out | 19 | 669 | 529 |
| mnar_out | 20 | 674 | 532 |
| mnar_out | 21 | 671 | 530 |
| mnar_out | 22 | 697 | 548 |
| mnar_out | 23 | 660 | 502 |
| mnar_out | 24 | 662 | 525 |
| mnar_out | 25 | 649 | 513 |
| mnar_out | 26 | 654 | 521 |
| mnar_out | 27 | 677 | 527 |
| mnar_out | 28 | 660 | 526 |
| mnar_out | 29 | 654 | 509 |
| mnar_out | 30 | 684 | 547 |

## Ranking metrics across completed replicates

| Mechanism | Score | Metric | Replicates | Mean | SD |
|---|---|---|---:|---:|---:|
| mcar | already_observed_footprint | pr_auc | 30 | 0.5166 | 0.0071 |
| mcar | already_observed_footprint | precision_at_k | 30 | 0.5182 | 0.0072 |
| mcar | already_observed_footprint | recall_at_k | 30 | 0.5182 | 0.0072 |
| mcar | already_observed_footprint | roc_auc | 30 | 0.5287 | 0.0113 |
| mcar | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.4936 | 0.0061 |
| mcar | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.4927 | 0.0065 |
| mcar | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.4927 | 0.0065 |
| mcar | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.4914 | 0.0059 |
| mcar | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.5799 | 0.0117 |
| mcar | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.5657 | 0.0129 |
| mcar | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.5657 | 0.0129 |
| mcar | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.5909 | 0.0107 |
| mcar | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.5207 | 0.0053 |
| mcar | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.5205 | 0.0069 |
| mcar | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.5205 | 0.0069 |
| mcar | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.5255 | 0.0057 |
| mcar | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.5350 | 0.0070 |
| mcar | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.5310 | 0.0084 |
| mcar | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.5310 | 0.0084 |
| mcar | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.5401 | 0.0067 |
| mcar | lifted_cn_total_mean | pr_auc | 30 | 0.5371 | 0.0072 |
| mcar | lifted_cn_total_mean | precision_at_k | 30 | 0.5339 | 0.0080 |
| mcar | lifted_cn_total_mean | recall_at_k | 30 | 0.5339 | 0.0080 |
| mcar | lifted_cn_total_mean | roc_auc | 30 | 0.5436 | 0.0068 |
| mcar | lifted_degree_product_mean | pr_auc | 30 | 0.5916 | 0.0128 |
| mcar | lifted_degree_product_mean | precision_at_k | 30 | 0.5744 | 0.0106 |
| mcar | lifted_degree_product_mean | recall_at_k | 30 | 0.5744 | 0.0106 |
| mcar | lifted_degree_product_mean | roc_auc | 30 | 0.6045 | 0.0108 |
| mcar | lifted_ii_mean | pr_auc | 30 | 0.4938 | 0.0056 |
| mcar | lifted_ii_mean | precision_at_k | 30 | 0.4928 | 0.0061 |
| mcar | lifted_ii_mean | recall_at_k | 30 | 0.4928 | 0.0061 |
| mcar | lifted_ii_mean | roc_auc | 30 | 0.4913 | 0.0058 |
| mcar | lifted_oi_mean | pr_auc | 30 | 0.5760 | 0.0114 |
| mcar | lifted_oi_mean | precision_at_k | 30 | 0.5646 | 0.0113 |
| mcar | lifted_oi_mean | recall_at_k | 30 | 0.5646 | 0.0113 |
| mcar | lifted_oi_mean | roc_auc | 30 | 0.5903 | 0.0107 |
| mcar | lifted_oo_mean | pr_auc | 30 | 0.5195 | 0.0047 |
| mcar | lifted_oo_mean | precision_at_k | 30 | 0.5208 | 0.0068 |
| mcar | lifted_oo_mean | recall_at_k | 30 | 0.5208 | 0.0068 |
| mcar | lifted_oo_mean | roc_auc | 30 | 0.5255 | 0.0054 |
| mcar | lifted_reverse_arc_mean | pr_auc | 30 | 0.4911 | 0.0082 |
| mcar | lifted_reverse_arc_mean | precision_at_k | 30 | 0.4848 | 0.0105 |
| mcar | lifted_reverse_arc_mean | recall_at_k | 30 | 0.4848 | 0.0105 |
| mcar | lifted_reverse_arc_mean | roc_auc | 30 | 0.4832 | 0.0126 |
| mnar_out | already_observed_footprint | pr_auc | 30 | 0.5082 | 0.0056 |
| mnar_out | already_observed_footprint | precision_at_k | 30 | 0.5093 | 0.0060 |
| mnar_out | already_observed_footprint | recall_at_k | 30 | 0.5093 | 0.0060 |
| mnar_out | already_observed_footprint | roc_auc | 30 | 0.5148 | 0.0095 |
| mnar_out | lifted_adamic_adar_ii_mean | pr_auc | 30 | 0.5034 | 0.0056 |
| mnar_out | lifted_adamic_adar_ii_mean | precision_at_k | 30 | 0.5018 | 0.0083 |
| mnar_out | lifted_adamic_adar_ii_mean | recall_at_k | 30 | 0.5018 | 0.0083 |
| mnar_out | lifted_adamic_adar_ii_mean | roc_auc | 30 | 0.5059 | 0.0066 |
| mnar_out | lifted_adamic_adar_oi_mean | pr_auc | 30 | 0.5448 | 0.0189 |
| mnar_out | lifted_adamic_adar_oi_mean | precision_at_k | 30 | 0.5444 | 0.0154 |
| mnar_out | lifted_adamic_adar_oi_mean | recall_at_k | 30 | 0.5444 | 0.0154 |
| mnar_out | lifted_adamic_adar_oi_mean | roc_auc | 30 | 0.5577 | 0.0211 |
| mnar_out | lifted_adamic_adar_oo_mean | pr_auc | 30 | 0.5149 | 0.0050 |
| mnar_out | lifted_adamic_adar_oo_mean | precision_at_k | 30 | 0.5152 | 0.0096 |
| mnar_out | lifted_adamic_adar_oo_mean | recall_at_k | 30 | 0.5152 | 0.0096 |
| mnar_out | lifted_adamic_adar_oo_mean | roc_auc | 30 | 0.5215 | 0.0090 |
| mnar_out | lifted_adamic_adar_total_mean | pr_auc | 30 | 0.5229 | 0.0085 |
| mnar_out | lifted_adamic_adar_total_mean | precision_at_k | 30 | 0.5262 | 0.0109 |
| mnar_out | lifted_adamic_adar_total_mean | recall_at_k | 30 | 0.5262 | 0.0109 |
| mnar_out | lifted_adamic_adar_total_mean | roc_auc | 30 | 0.5334 | 0.0110 |
| mnar_out | lifted_cn_total_mean | pr_auc | 30 | 0.5232 | 0.0088 |
| mnar_out | lifted_cn_total_mean | precision_at_k | 30 | 0.5267 | 0.0107 |
| mnar_out | lifted_cn_total_mean | recall_at_k | 30 | 0.5267 | 0.0107 |
| mnar_out | lifted_cn_total_mean | roc_auc | 30 | 0.5346 | 0.0114 |
| mnar_out | lifted_degree_product_mean | pr_auc | 30 | 0.5600 | 0.0169 |
| mnar_out | lifted_degree_product_mean | precision_at_k | 30 | 0.5479 | 0.0147 |
| mnar_out | lifted_degree_product_mean | recall_at_k | 30 | 0.5479 | 0.0147 |
| mnar_out | lifted_degree_product_mean | roc_auc | 30 | 0.5683 | 0.0207 |
| mnar_out | lifted_ii_mean | pr_auc | 30 | 0.5031 | 0.0053 |
| mnar_out | lifted_ii_mean | precision_at_k | 30 | 0.5001 | 0.0079 |
| mnar_out | lifted_ii_mean | recall_at_k | 30 | 0.5001 | 0.0079 |
| mnar_out | lifted_ii_mean | roc_auc | 30 | 0.5056 | 0.0065 |
| mnar_out | lifted_oi_mean | pr_auc | 30 | 0.5414 | 0.0179 |
| mnar_out | lifted_oi_mean | precision_at_k | 30 | 0.5434 | 0.0160 |
| mnar_out | lifted_oi_mean | recall_at_k | 30 | 0.5434 | 0.0160 |
| mnar_out | lifted_oi_mean | roc_auc | 30 | 0.5560 | 0.0209 |
| mnar_out | lifted_oo_mean | pr_auc | 30 | 0.5140 | 0.0048 |
| mnar_out | lifted_oo_mean | precision_at_k | 30 | 0.5141 | 0.0092 |
| mnar_out | lifted_oo_mean | recall_at_k | 30 | 0.5141 | 0.0092 |
| mnar_out | lifted_oo_mean | roc_auc | 30 | 0.5212 | 0.0086 |
| mnar_out | lifted_reverse_arc_mean | pr_auc | 30 | 0.5066 | 0.0080 |
| mnar_out | lifted_reverse_arc_mean | precision_at_k | 30 | 0.5034 | 0.0089 |
| mnar_out | lifted_reverse_arc_mean | recall_at_k | 30 | 0.5034 | 0.0089 |
| mnar_out | lifted_reverse_arc_mean | roc_auc | 30 | 0.5071 | 0.0106 |
